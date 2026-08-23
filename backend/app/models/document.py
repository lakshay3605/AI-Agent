"""Document data models."""

from typing import List, Optional
from pydantic import BaseModel, Field


class PageContent(BaseModel):
    """Extracted content for a single PDF page."""
    page_number: int = Field(..., description="1-indexed page number")
    text: str = Field(..., description="Raw extracted text from page")


class DocumentMetadata(BaseModel):
    """Metadata extracted and classified for a PDF document."""
    filename: str
    title: str
    doc_type: str = Field(..., description="policy | sop | customer_agreement | operations_guide")
    status: str = Field(default="current", description="current | deprecated")
    customer: Optional[str] = Field(default=None, description="Customer name if customer-specific document")
    page_count: int


class ParsedDocument(BaseModel):
    """Complete parsed document record."""
    metadata: DocumentMetadata
    full_text: str
    pages: List[PageContent]
