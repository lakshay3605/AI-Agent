"""Embedding provider using OpenAI embeddings."""

import logging
from abc import ABC, abstractmethod
from typing import List

from app.core.config import settings

logger = logging.getLogger("parcelpilot.embeddings")


class BaseEmbeddingProvider(ABC):

    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        pass

    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        pass


class OpenAIEmbeddingProvider(BaseEmbeddingProvider):
    """Lightweight OpenAI embedding provider."""

    def __init__(
        self,
        model_name: str = "text-embedding-3-small",
    ):
        self.model_name = model_name
        self._client = None

    @property
    def client(self):
        if self._client is None:
            from openai import OpenAI

            if not settings.OPENAI_API_KEY:
                raise RuntimeError("OPENAI_API_KEY is not configured.")

            self._client = OpenAI(
                api_key=settings.OPENAI_API_KEY
            )

        return self._client

    def embed_documents(
        self,
        texts: List[str],
    ) -> List[List[float]]:
        if not texts:
            return []

        response = self.client.embeddings.create(
            model=self.model_name,
            input=texts,
        )

        return [item.embedding for item in response.data]

    def embed_query(
        self,
        text: str,
    ) -> List[float]:
        response = self.client.embeddings.create(
            model=self.model_name,
            input=text,
        )

        return response.data[0].embedding


class SentenceTransformerEmbeddingProvider(BaseEmbeddingProvider):
    """Local SentenceTransformer embedding provider (e.g. BAAI/bge-small-en-v1.5)."""

    def __init__(self, model_name: str = settings.EMBEDDING_MODEL_NAME):
        self.model_name = model_name
        self._model = None

    @property
    def model(self):
        if self._model is None:
            import os
            os.environ.setdefault("TORCH_NUM_THREADS", "1")
            os.environ.setdefault("OMP_NUM_THREADS", "1")
            os.environ.setdefault("MKL_NUM_THREADS", "1")
            try:
                import torch
                torch.set_num_threads(1)
                try:
                    torch.set_num_interop_threads(1)
                except Exception:
                    pass
            except ImportError:
                pass

            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name, device="cpu")
        return self._model

    def preload(self):
        """Warm up model into memory during container startup."""
        _ = self.model

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        import torch
        with torch.no_grad():
            embeddings = self.model.encode(
                texts,
                convert_to_numpy=True,
                show_progress_bar=False,
                batch_size=16,
            )
        return embeddings.tolist()

    def embed_query(self, text: str) -> List[float]:
        import torch
        with torch.no_grad():
            embedding = self.model.encode(
                text,
                convert_to_numpy=True,
                show_progress_bar=False,
            )
        return embedding.tolist()


class GeminiEmbeddingProvider(BaseEmbeddingProvider):
    """Zero-memory Gemini API embedding provider (100% Free Tier)."""

    def __init__(self, model_name: str = "models/text-embedding-004"):
        self.model_name = model_name
        self._embeddings = None

    @property
    def embeddings(self):
        if self._embeddings is None:
            if not settings.GEMINI_API_KEY:
                raise RuntimeError("GEMINI_API_KEY is not configured.")
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
            self._embeddings = GoogleGenerativeAIEmbeddings(
                model=self.model_name,
                google_api_key=settings.GEMINI_API_KEY
            )
        return self._embeddings

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        return self.embeddings.embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        return self.embeddings.embed_query(text)


def get_default_embedding_provider() -> BaseEmbeddingProvider:
    """
    Factory returning appropriate embedding provider.
    Auto-selects lightweight API embeddings (OpenAI or Gemini) if API keys are configured,
    preventing PyTorch OOM crashes on Render 512MB RAM instances.
    """
    provider = getattr(settings, "EMBEDDING_PROVIDER", "auto").lower()
    if provider == "openai":
        return OpenAIEmbeddingProvider()
    elif provider == "gemini":
        return GeminiEmbeddingProvider()
    elif provider == "sentence_transformer":
        return SentenceTransformerEmbeddingProvider()

    # Automatic selection: Use API provider if key is configured (0 MB PyTorch RAM)
    if settings.OPENAI_API_KEY:
        logger.info("Auto-selected OpenAIEmbeddingProvider for zero-memory vector retrieval.")
        return OpenAIEmbeddingProvider()
    elif settings.GEMINI_API_KEY:
        logger.info("Auto-selected GeminiEmbeddingProvider for zero-memory vector retrieval.")
        return GeminiEmbeddingProvider()

    logger.info("Defaulting to SentenceTransformerEmbeddingProvider.")
    return SentenceTransformerEmbeddingProvider()