"""Abstract embedding provider and SentenceTransformers implementation."""

import logging
from abc import ABC, abstractmethod
from typing import List

from app.core.config import settings

logger = logging.getLogger("parcelpilot.embeddings")


class BaseEmbeddingProvider(ABC):
    """Abstract interface for generating text embeddings."""

    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embedding vectors for a list of document texts."""
        pass

    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        """Generate embedding vector for a single query text."""
        pass


class SentenceTransformerEmbeddingProvider(BaseEmbeddingProvider):
    """SentenceTransformers local embedding provider using BAAI/bge-small-en-v1.5."""

    def __init__(self, model_name: str = settings.EMBEDDING_MODEL_NAME):
        self.model_name = model_name
        self._model = None

    @property
    def model(self):
        """Lazy load model on first usage."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info(f"Loading SentenceTransformer embedding model: {self.model_name}")
                self._model = SentenceTransformer(self.model_name)
            except Exception as e:
                logger.error(f"Failed to load embedding model {self.model_name}: {e}")
                # Fallback model loading if BGE download fails or offline
                from sentence_transformers import SentenceTransformer
                fallback = "all-MiniLM-L6-v2"
                logger.info(f"Attempting fallback embedding model: {fallback}")
                self._model = SentenceTransformer(fallback)
        return self._model

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for text chunks."""
        if not texts:
            return []
        embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        return embeddings.tolist()

    def embed_query(self, text: str) -> List[float]:
        """Generate embedding for query string."""
        embedding = self.model.encode(text, convert_to_numpy=True, show_progress_bar=False)
        return embedding.tolist()
