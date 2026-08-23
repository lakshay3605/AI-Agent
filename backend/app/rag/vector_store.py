"""ChromaDB Vector Store Manager."""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.core.config import settings
from app.rag.chunker import TextChunk
from app.rag.embeddings import BaseEmbeddingProvider, SentenceTransformerEmbeddingProvider

logger = logging.getLogger("parcelpilot.vector_store")


_chroma_client_cache: Dict[str, Any] = {}


def get_chroma_client(persist_path: Path) -> chromadb.ClientAPI:
    path_str = str(persist_path.resolve())
    if path_str not in _chroma_client_cache:
        _chroma_client_cache[path_str] = chromadb.PersistentClient(
            path=path_str,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
    return _chroma_client_cache[path_str]


class VectorStoreManager:
    """Manages persistent ChromaDB vector store collection and operations."""

    def __init__(
        self,
        persist_directory: str = settings.CHROMA_PERSIST_DIR,
        collection_name: str = settings.CHROMA_COLLECTION_NAME,
        embedding_provider: Optional[BaseEmbeddingProvider] = None,
    ):
        self.persist_path = Path(persist_directory).resolve()
        self.persist_path.mkdir(parents=True, exist_ok=True)
        self.collection_name = collection_name
        self.embedding_provider = embedding_provider or SentenceTransformerEmbeddingProvider()

        logger.info(f"Initializing ChromaDB client at persistent path: {self.persist_path}")
        self.client = get_chroma_client(self.persist_path)
        self._collection = None

    def get_collection(self):
        """Retrieve or create the ChromaDB collection."""
        if self._collection is None:
            self._collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
        return self._collection

    def add_chunks(self, chunks: List[TextChunk]) -> int:
        """Embed and add a list of TextChunks into Chroma collection."""
        if not chunks:
            return 0

        collection = self.get_collection()

        ids = [c.chunk_id for c in chunks]
        texts = [c.text for c in chunks]
        metadatas = [c.metadata for c in chunks]

        # Generate embeddings via provider abstraction
        embeddings = self.embedding_provider.embed_documents(texts)

        # Upsert into ChromaDB
        collection.upsert(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
        )

        logger.info(f"Successfully upserted {len(chunks)} chunks into collection '{self.collection_name}'")
        return len(chunks)

    def query(
        self, 
        query_text: str, 
        n_results: int = 5, 
        where_filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Query vector store using semantic search with optional metadata filtering.
        """
        collection = self.get_collection()
        if collection.count() == 0:
            logger.warning(f"Vector store collection '{self.collection_name}' is empty.")
            return []

        query_embedding = self.embedding_provider.embed_query(query_text)

        kwargs = {
            "query_embeddings": [query_embedding],
            "n_results": min(n_results, collection.count()),
            "include": ["documents", "metadatas", "distances"],
        }
        if where_filter:
            kwargs["where"] = where_filter

        results = collection.query(**kwargs)

        processed_results: List[Dict[str, Any]] = []
        if results and results.get("documents") and len(results["documents"]) > 0:
            docs = results["documents"][0]
            metas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(docs)
            dists = results["distances"][0] if results.get("distances") else [0.0] * len(docs)

            for text, meta, dist in zip(docs, metas, dists):
                # Convert cosine distance to similarity score (0.0 to 1.0)
                score = round(max(0.0, 1.0 - (dist / 2.0)), 3)
                processed_results.append({
                    "text": text,
                    "score": score,
                    "document": meta.get("document_filename", ""),
                    "page": meta.get("page_number", 1),
                    "metadata": meta,
                })

        return processed_results

    def reset_collection(self) -> None:
        """Delete existing collection for index rebuilding."""
        try:
            self.client.delete_collection(name=self.collection_name)
            self._collection = None
            logger.info(f"Deleted collection '{self.collection_name}' for rebuilding.")
        except Exception:
            pass
