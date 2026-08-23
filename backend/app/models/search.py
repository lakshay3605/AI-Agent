"""Keyword search result models."""

from typing import List, Optional
from pydantic import BaseModel, Field


class SearchResultItem(BaseModel):
    """Matched document snippet record."""
    document_filename: str
    document_title: str
    doc_type: str
    status: str
    page_number: Optional[int] = Field(default=None, description="Matching page number")
    snippet: str = Field(..., description="Matched text snippet with surrounding context")
    relevance_score: float = Field(default=1.0, description="Basic match score")


class SearchResponse(BaseModel):
    """Keyword search API response."""
    query: str
    total_results: int
    results: List[SearchResultItem]
