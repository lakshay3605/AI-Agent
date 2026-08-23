"""Semantic RAG Search API Endpoint."""

from typing import Optional
from fastapi import APIRouter, Query

from app.rag.retriever import CustomerAwareRetriever, RetrieverResponse

router = APIRouter()
retriever = CustomerAwareRetriever()


@router.get("/search", response_model=RetrieverResponse, summary="Perform semantic RAG document search")
async def semantic_search(
    q: str = Query(..., description="Query string (e.g. 'cancellation fee')"),
    customer: Optional[str] = Query(default=None, description="Optional customer filter (e.g. 'Northstar Logistics')"),
    status: Optional[str] = Query(default=None, description="Optional status filter (e.g. 'current')"),
    limit: int = Query(default=5, ge=1, le=20, description="Top-k number of relevant passages to return"),
) -> RetrieverResponse:
    """
    Perform semantic vector search across parsed PDF chunks using BAAI/bge-small-en-v1.5 embeddings and ChromaDB.
    Returns matching text passages, relevance scores, page numbers, and document authority metadata.
    """
    return retriever.retrieve(
        query=q,
        customer=customer,
        status=status,
        limit=limit,
    )
