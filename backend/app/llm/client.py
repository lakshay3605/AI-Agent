"""Dedicated LLM Client Factory Service for ParcelPilot AI using OpenAI Chat Models."""

import os
import logging
from typing import Optional, Union
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import settings

logger = logging.getLogger("parcelpilot.llm")

# Load environment variables from .env files
base_dir = settings.BASE_DIR
load_dotenv(os.path.join(base_dir, "backend", ".env"), override=True)
load_dotenv(os.path.join(base_dir, ".env"), override=True)


class LLMConfigError(Exception):
    """Custom exception raised when LLM provider configuration or API key is missing/invalid."""
    pass


_chat_model_cache: dict = {}


def get_chat_model(
    model_name: Optional[str] = None,
    temperature: float = 0.0,
    api_key: Optional[str] = None,
) -> Union[ChatOpenAI, ChatGoogleGenerativeAI]:
    """
    Initialize and return a Chat model instance (defaulting to ChatOpenAI).
    Reads configuration from environment variables / settings without leaking secrets in logs.
    """
    provider = os.getenv("LLM_PROVIDER", getattr(settings, "LLM_PROVIDER", "openai")).lower()

    if provider == "gemini":
        selected_model = model_name or os.getenv("GEMINI_MODEL", getattr(settings, "GEMINI_MODEL", "gemini-3.5-flash-lite"))
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

    # Default provider: OpenAI
    selected_model = model_name or os.getenv("OPENAI_MODEL", getattr(settings, "OPENAI_MODEL", "gpt-5-nano"))
    resolved_api_key = (
        api_key
        or os.getenv("OPENAI_API_KEY")
        or getattr(settings, "OPENAI_API_KEY", None)
    )

    if not resolved_api_key or str(resolved_api_key).strip() in ["", "your-openai-api-key-here", "placeholder"]:
        raise LLMConfigError(
            "OPENAI_API_KEY is not set or contains a default placeholder. "
            "Please set a valid OPENAI_API_KEY in your environment or .env file."
        )

    cache_key = f"{provider}:{selected_model}:{temperature}"
    if cache_key in _chat_model_cache:
        return _chat_model_cache[cache_key]

    logger.info(f"Initializing ChatOpenAI client with provider='{provider}', model='{selected_model}'")

    model_instance = ChatOpenAI(
        model=selected_model,
        openai_api_key=resolved_api_key,
        temperature=temperature,
    )
    
    _chat_model_cache[cache_key] = model_instance
    return model_instance


def clear_llm_cache() -> None:
    """Helper method to clear cached LLM instances for testing."""
    global _chat_model_cache
    _chat_model_cache = {}
