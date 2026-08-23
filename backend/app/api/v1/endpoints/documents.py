"""Documents API endpoints."""

from typing import List
from fastapi import APIRouter, HTTPException, Depends

from app.models.document import DocumentMetadata, ParsedDocument
from app.services.data_service import DataService, get_data_service

router = APIRouter()


@router.get("/documents", response_model=List[DocumentMetadata], summary="List all indexed documents")
async def list_documents(ds: DataService = Depends(get_data_service)) -> List[DocumentMetadata]:
    """Retrieve metadata list of all indexed PDF documents."""
    return ds.get_all_documents()


@router.get("/documents/{document_name}", response_model=ParsedDocument, summary="Get document details")
async def get_document(
    document_name: str, 
    ds: DataService = Depends(get_data_service)
) -> ParsedDocument:
    """Retrieve full content, metadata, and page list for a specific document."""
    doc = ds.get_document_by_name(document_name)
    if not doc:
        raise HTTPException(
            status_code=404, 
            detail=f"Document '{document_name}' not found."
        )
    return doc
