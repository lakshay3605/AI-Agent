"""Application settings and configuration management."""

import os
import json
from typing import List, Any
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application Settings loaded from environment variables."""
    PROJECT_NAME: str = "ParcelPilot AI Agent API"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    API_V1_STR: str = "/api/v1"
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> List[str]:
        if isinstance(v, str):
            v = v.strip()
            if v.startswith("[") and v.endswith("]"):
                return json.loads(v)
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return ["http://localhost:3000", "http://127.0.0.1:3000"]

    # RAG Settings
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DATA_DIR: str = os.path.join(os.path.dirname(BASE_DIR), "data")
    CHUNK_SIZE: int = 600
    CHUNK_OVERLAP: int = 100
    EMBEDDING_PROVIDER: str = "auto"
    EMBEDDING_MODEL_NAME: str = "BAAI/bge-small-en-v1.5"
    CHROMA_PERSIST_DIR: str = os.path.join(BASE_DIR, "storage", "chroma")
    CHROMA_COLLECTION_NAME: str = "parcelpilot_docs"

    # LLM Settings
    LLM_PROVIDER: str = "openai"
    OPENAI_MODEL: str = "gpt-5-nano"
    OPENAI_API_KEY: str | None = None
    GEMINI_MODEL: str = "gemini-3.5-flash-lite"
    GEMINI_API_KEY: str | None = None

    model_config = SettingsConfigDict(
        env_file=(
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "backend", ".env"),
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), ".env"),
            ".env",
        ),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
