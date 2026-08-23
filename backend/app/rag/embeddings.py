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
        pass

    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        pass


class SentenceTransformerEmbeddingProvider(BaseEmbeddingProvider):
    """SentenceTransformers local embedding provider."""

    _shared_models = {}

    def __init__(self, model_name: str = settings.EMBEDDING_MODEL_NAME):
        self.model_name = model_name

    @property
    def model(self):
        """Load the embedding model once and reuse it."""
        if self.model_name not in self._shared_models:
            try:
                from sentence_transformers import SentenceTransformer

                logger.info(
                    f"Loading SentenceTransformer embedding model: {self.model_name}"
                )

                self._shared_models[self.model_name] = SentenceTransformer(
                    self.model_name
                )

            except Exception as e:
                logger.error(
                    f"Failed to load embedding model {self.model_name}: {e}"
                )

                fallback = "all-MiniLM-L6-v2"

                if fallback not in self._shared_models:
                    from sentence_transformers import SentenceTransformer

                    logger.info(
                        f"Attempting fallback embedding model: {fallback}"
                    )

                    self._shared_models[fallback] = SentenceTransformer(
                        fallback
                    )

                self.model_name = fallback

        return self._shared_models[self.model_name]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for text chunks."""
        if not texts:
            return []

        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=False,
        )

        return embeddings.tolist()

    def embed_query(self, text: str) -> List[float]:
        """Generate embedding for query string."""
        embedding = self.model.encode(
            text,
            convert_to_numpy=True,
            show_progress_bar=False,
        )

        return embedding.tolist()