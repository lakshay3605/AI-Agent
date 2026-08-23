"""Dedicated LLM Client Factory Service for ParcelPilot AI using Google Gemini with Quota Fallback."""

import os
import logging
from typing import Optional
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import settings

logger = logging.getLogger("parcelpilot.llm")

# Load environment variables from .env files
base_dir = settings.BASE_DIR
load_dotenv(os.path.join(base_dir, "backend", ".env"))
load_dotenv(os.path.join(base_dir, ".env"))


class LLMConfigError(Exception):
    """Custom exception raised when LLM provider configuration or API key is missing/invalid."""
    pass


_chat_model_cache: dict = {}


def get_chat_model(
    model_name: Optional[str] = None,
    temperature: float = 0.0,
    api_key: Optional[str] = None,
) -> ChatGoogleGenerativeAI:
    """
    Initialize and return a ChatGoogleGenerativeAI instance.
    Reads configuration from environment variables / settings without leaking secrets in logs.
    """
    provider = os.getenv("LLM_PROVIDER", settings.LLM_PROVIDER).lower()
    selected_model = model_name or os.getenv("GEMINI_MODEL", getattr(settings, "GEMINI_MODEL", "gemini-2.5-flash"))
    resolved_api_key = (
        api_key
        or os.getenv("GEMINI_API_KEY")
        or os.getenv("GOOGLE_API_KEY")
        or getattr(settings, "GEMINI_API_KEY", None)
    )

    if not resolved_api_key or str(resolved_api_key).strip() in ["", "your-gemini-api-key-here", "placeholder"]:
        raise LLMConfigError(
            "GEMINI_API_KEY is not set or contains a default placeholder. "
            "Please set a valid GEMINI_API_KEY in your environment or .env file."
        )

    cache_key = f"{provider}:{selected_model}:{temperature}"
    if cache_key in _chat_model_cache:
        return _chat_model_cache[cache_key]

    logger.info(f"Initializing ChatGoogleGenerativeAI client with provider='{provider}', model='{selected_model}'")

    model_instance = ChatGoogleGenerativeAI(
        model=selected_model,
        google_api_key=resolved_api_key,
        temperature=temperature,
    )
    
    _chat_model_cache[cache_key] = model_instance
    return model_instance


def clear_llm_cache() -> None:
    """Helper method to clear cached LLM instances for testing."""
    global _chat_model_cache
    _chat_model_cache = {}
