"""Text Chunker with metadata preservation & authority tagging."""

import logging
from typing import List, Dict, Any
from pydantic import BaseModel, Field

from app.models.document import ParsedDocument
from app.core.config import settings

logger = logging.getLogger("parcelpilot.chunker")


class TextChunk(BaseModel):
    """Structured text chunk with comprehensive metadata."""
    chunk_id: str
    text: str
    metadata: Dict[str, Any] = Field(
        ...,
        description=(
            "Must contain document_filename, document_title, document_type, status, "
            "customer, page_number, chunk_index, authority"
        )
    )


def determine_authority(doc_type: str, status: str, customer: str | None) -> str:
    """
    Determine document authority classification rule.
    
    Rules:
    - Deprecated documents -> 'deprecated'
    - Customer Agreements -> 'customer_agreement'
    - Current SOPs -> 'sop'
    - Current Policies -> 'general_policy'
    - Operations guides -> 'operations'
    """
    if status == "deprecated":
        return "deprecated"
    
    if doc_type == "customer_agreement":
        return "customer_agreement"
    elif doc_type == "sop":
        return "sop"
    elif doc_type == "policy":
        return "general_policy"
    elif doc_type == "operations_guide":
        return "operations"
    
    return "general_policy"


def chunk_document(
    doc: ParsedDocument, 
    chunk_size: int = settings.CHUNK_SIZE, 
    overlap: int = settings.CHUNK_OVERLAP
) -> List[TextChunk]:
    """
    Chunk a parsed document into overlapping text chunks preserving page numbers and metadata.
    """
    chunks: List[TextChunk] = []
    global_chunk_idx = 0

    authority = determine_authority(
        doc_type=doc.metadata.doc_type,
        status=doc.metadata.status,
        customer=doc.metadata.customer
    )

    for page in doc.pages:
        page_text = page.text.strip()
        if not page_text:
            continue

        # If page text is small enough, keep as single page chunk
        if len(page_text) <= chunk_size:
            chunk_id = f"{doc.metadata.filename}:p{page.page_number}:c{global_chunk_idx}"
            metadata = {
                "document_filename": doc.metadata.filename,
                "document_title": doc.metadata.title,
                "document_type": doc.metadata.doc_type,
                "status": doc.metadata.status,
                "customer": doc.metadata.customer or "",
                "page_number": page.page_number,
                "chunk_index": global_chunk_idx,
                "authority": authority,
            }
            chunks.append(TextChunk(chunk_id=chunk_id, text=page_text, metadata=metadata))
            global_chunk_idx += 1
        else:
            # Split page text into overlapping windows
            start = 0
            text_len = len(page_text)

            while start < text_len:
                end = min(start + chunk_size, text_len)
                
                # Adjust end to nearest space boundary if possible
                if end < text_len:
                    space_idx = page_text.rfind(" ", start + int(chunk_size * 0.7), end)
                    if space_idx != -1:
                        end = space_idx

                chunk_text = page_text[start:end].strip()
                if chunk_text:
                    chunk_id = f"{doc.metadata.filename}:p{page.page_number}:c{global_chunk_idx}"
                    metadata = {
                        "document_filename": doc.metadata.filename,
                        "document_title": doc.metadata.title,
                        "document_type": doc.metadata.doc_type,
                        "status": doc.metadata.status,
                        "customer": doc.metadata.customer or "",
                        "page_number": page.page_number,
                        "chunk_index": global_chunk_idx,
                        "authority": authority,
                    }
                    chunks.append(TextChunk(chunk_id=chunk_id, text=chunk_text, metadata=metadata))
                    global_chunk_idx += 1

                if end >= text_len:
                    break
                start = end - overlap

    return chunks
