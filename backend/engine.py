# ─────────────────────────────────────────────────────────────────────────────
# Engine wiring — builds the TaxFormAgent that the API serves.
#
# Nothing here is per-request. build_agent() is called once, at startup.
# ─────────────────────────────────────────────────────────────────────────────

import os

from dotenv import load_dotenv

from tax_form_agent.agent import TaxFormAgent
from tax_form_agent.form_knowledge import FormKnowledge
from tax_form_agent.llm_client import LLMClient

load_dotenv()

DEFAULT_MODEL = "gpt-4o-mini"

# Absolute path, derived from this file's location. A bare "data/..." would
# resolve against whatever directory uvicorn was started from — which works
# locally and fails on Render.
DATA_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "data",
    "COMPLETE_FORM_STRUCTURE.json",
)


def build_agent() -> TaxFormAgent:
    """Load the form structure and wire up the agent.

    Raises on missing config so a misconfigured deploy dies at boot instead of
    looking healthy and failing on the first user message.
    """
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Put it in backend/.env for local runs, "
            "or in the service's environment variables when deployed."
        )

    if not os.path.exists(DATA_FILE):
        raise RuntimeError(f"Form structure not found at {DATA_FILE}")

    fk = FormKnowledge(DATA_FILE)
    llm = LLMClient(
        api_key=api_key,
        model=os.environ.get("OPENAI_MODEL", DEFAULT_MODEL),
    )
    return TaxFormAgent(fk, llm)
