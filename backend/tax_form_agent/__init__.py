"""
Tax Form Agent - AI assistant for German tax registration form.
"""
from .form_knowledge import FormKnowledge, FormCursor
from .llm_client import LLMClient
from .agent import TaxFormAgent

__version__ = "1.0.0"
__all__ = ["FormKnowledge", "FormCursor", "LLMClient", "TaxFormAgent"]