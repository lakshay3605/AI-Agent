"""Customer-aware Semantic Retriever."""

import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from app.rag.vector_store import VectorStoreManager

logger = logging.getLogger("parcelpilot.retriever")


class RetrieverResult(BaseModel):
    """Structured semantic retrieval item."""
    text: str
    score: float
    document: str
    page: int
    metadata: Dict[str, Any]


class RetrieverResponse(BaseModel):
    """Structured semantic retrieval API response."""
    query: str
    total_results: int
    results: List[RetrieverResult]


class CustomerAwareRetriever:
    """Retriever handling vector similarity queries with customer & document authority metadata filtering."""

    def __init__(self, vector_store: Optional[VectorStoreManager] = None):
        self.vector_store = vector_store or VectorStoreManager()

    def retrieve(
        self, 
        query: str, 
        customer: Optional[str] = None, 
        limit: int = 5,
        status: Optional[str] = None
    ) -> RetrieverResponse:
        """
        Execute semantic retrieval with optional customer and status filters.
        """
        where_filter: Dict[str, Any] = {}

        if customer:
            # Match customer name or general non-customer documents
            where_filter["$or"] = [
                {"customer": customer},
                {"customer": ""},
            ]

        if status:
            where_filter["status"] = status

        raw_results = self.vector_store.query(
            query_text=query,
            n_results=limit,
            where_filter=where_filter if where_filter else None,
        )

        results: List[RetrieverResult] = []
        for r in raw_results:
            results.append(
                RetrieverResult(
                    text=r["text"],
                    score=r["score"],
                    document=r["document"],
                    page=r["page"],
                    metadata=r["metadata"],
                )
            )

        return RetrieverResponse(
            query=query,
            total_results=len(results),
            results=results,
        )
