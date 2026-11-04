import os
import secrets
import uuid
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from engine import build_agent

LANGUAGES = ("en", "de")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Built once. FormKnowledge parses a 393 KB JSON file and builds its search
    # indexes, so this must not happen per request. A single agent serves every
    # user — it keeps one Session per thread_id internally (agent.py:1162).
    app.state.agent = build_agent()
    # The key check disables itself when unconfigured, so say which it is —
    # otherwise a silently-open endpoint looks identical to a protected one.
    print("API key check:",
          "ENABLED" if os.environ.get("APP_API_KEY", "").strip() else "DISABLED")
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://helferei-ashy.vercel.app",
        "https://helferei-git-frontend-salim-oseis-projects.vercel.app",
    ],
    allow_origin_regex=r"https://helferei-git-.*-salim-oseis-projects\.vercel\.app",
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    # Omit on the first message; the response hands back an id to send with
    # every message after that. It is what keeps the user's position in the
    # form and their conversation history.
    session_id: str | None = None
    lang: str | None = None


class ChatResponse(BaseModel):
    answer: str
    session_id: str
    # "Abschnitt 7: Angaben zum Unternehmen > Adresse im Inland" — split out of
    # the reply so the frontend can render a location bar, and so `answer` does
    # not repeat it.
    breadcrumb: str


def _strip_breadcrumb(answer: str) -> str:
    """Remove the leading "📍 <breadcrumb>\n\n" that chat() adds to most replies.

    The breadcrumb is returned in its own field, so leaving it in the text would
    show the user their location twice. Not every reply carries the prefix (the
    /lang acknowledgement and the cross-section field notice do not), so this
    only strips what is there.
    """
    if answer.startswith("📍") and "\n\n" in answer:
        return answer.partition("\n\n")[2].strip()
    return answer


def _strip_nav_tip(answer: str) -> str:
    """Drop the trailing "🧭 To navigate the form..." tip.

    FOLLOWUP_SYSTEM orders the model to end every follow-up answer with it
    (agent.py:3176) as a terminator, so its output shape stays predictable. It
    was never meant to be read on every turn — the desktop app strips it the
    same way (src/tax_form_agent/gui.py:897).

    rfind, not a regex: if the model emits 🧭 mid-answer, a greedy regex would
    discard everything after it. Only the last occurrence counts, and only when
    it looks like a tail rather than part of the body.
    """
    idx = answer.rfind("🧭")
    if idx < 0 or len(answer) - idx > 400:
        return answer
    nl = answer.rfind("\n", 0, idx)
    if nl >= 0:
        # The tip starts on its own line — cut from that line onward.
        stripped = answer[:nl + 1].rstrip()
    else:
        # No newline before it: keep whatever body precedes it on the same
        # line, or a short reply would lose its entire content.
        stripped = answer[:idx].rstrip()
    # If the tip was the whole reply, keep it — better than a blank bubble.
    return stripped or answer


def require_api_key(x_api_key: str | None = Header(None)):
    """Reject requests that do not carry our shared secret.

    Attached per endpoint rather than as middleware, so `/` stays reachable for
    Render's health check and any uptime pinger. Every new endpoint should take
    this dependency; `/` is the only intentional exception.

    Disabled while APP_API_KEY is unset, which lets the backend ship before the
    frontend starts sending the header. `compare_digest` rather than `==`:
    `==` short-circuits on the first wrong byte, so response timing would leak
    the key one character at a time.

    Read from os.environ here rather than at import time — load_dotenv() runs
    when `engine` is imported, so a module-level constant would depend on the
    order of statements in this file.
    """
    expected = os.environ.get("APP_API_KEY", "").strip()
    if not expected:
        return
    if not x_api_key or not secrets.compare_digest(x_api_key, expected):
        raise HTTPException(status_code=401, detail="invalid api key")


@app.get("/")
def root():
    return {"message": "Hello from Helferei Backend, test rendering a branch"}

#Added to support cronjob
@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse,
          dependencies=[Depends(require_api_key)])
def chat(request: ChatRequest):
    # Deliberately `def`, not `async def`: TaxFormAgent.chat() blocks while it
    # waits on OpenAI. Declared async, it would stall the event loop and every
    # other request with it. FastAPI runs a plain `def` in a threadpool.
    message = request.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="message must not be empty")

    if request.lang is not None and request.lang not in LANGUAGES:
        raise HTTPException(
            status_code=400,
            detail=f"lang must be one of {LANGUAGES}",
        )

    agent = app.state.agent
    session_id = request.session_id or str(uuid.uuid4())

    if request.lang:
        agent.set_lang(request.lang, session_id)

    try:
        answer = agent.chat(message, thread_id=session_id)
    except RuntimeError as e:
        # LLMClient raises RuntimeError for API errors and timeouts. Surface it
        # as a gateway failure rather than a 500 with a stack trace.
        raise HTTPException(status_code=502, detail=f"AI request failed: {e}")

    return ChatResponse(
        answer=_strip_nav_tip(_strip_breadcrumb(answer)),
        session_id=session_id,
        # After chat(), never before: chat() moves the cursor as a side effect.
        breadcrumb=agent.get_breadcrumb(session_id),
    )
