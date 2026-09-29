import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
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
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://helferei-ashy.vercel.app",
        "https://helferei-git-frontend-salim-oseis-projects.vercel.app",
    ],
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


@app.get("/")
def root():
    return {"message": "Hello from Helferei Backend, test rendering a branch"}


@app.post("/chat", response_model=ChatResponse)
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
        answer=_strip_breadcrumb(answer),
        session_id=session_id,
        # After chat(), never before: chat() moves the cursor as a side effect.
        breadcrumb=agent.get_breadcrumb(session_id),
    )
