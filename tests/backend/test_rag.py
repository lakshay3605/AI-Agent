"""Comprehensive unit tests for Step 4 RAG pipeline."""

import sys
from pathlib import Path
import pytest

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from app.main import app
from app.models.document import ParsedDocument, DocumentMetadata, PageContent
from app.rag.chunker import chunk_document, determine_authority
from app.rag.embeddings import SentenceTransformerEmbeddingProvider
from app.rag.vector_store import VectorStoreManager
from app.rag.retriever import CustomerAwareRetriever
from app.services.data_service import get_data_service

client = TestClient(app)


def test_no_hardcoded_seeds_in_data_service():
    """Verify that DataService does NOT create hardcoded seed records when files are missing."""
    ds = get_data_service()
    # When data/ directory does not have Excel workbook, orders/customers/tickets should be authentic empty dicts
    # rather than hardcoded fake data
    assert isinstance(ds.orders, dict)
    assert isinstance(ds.customers, dict)
    assert isinstance(ds.tickets, dict)
    # Check that fallback method is completely gone
    assert not hasattr(ds, "_seed_fallback_defaults")


def test_authority_determination_rules():
    """Verify authority rules logic for metadata tagging."""
    assert determine_authority("customer_agreement", "current", "Northstar Logistics") == "customer_agreement"
    assert determine_authority("sop", "current", None) == "sop"
    assert determine_authority("policy", "current", None) == "general_policy"
    assert determine_authority("operations_guide", "current", None) == "operations"
    assert determine_authority("policy", "deprecated", None) == "deprecated"


def test_chunker_creation_and_metadata_preservation():
    """Test text chunker creates overlapping chunks and attaches all required metadata."""
    sample_doc = ParsedDocument(
        metadata=DocumentMetadata(
            filename="01_Support_Policy_v3_CURRENT.pdf",
            title="Support Policy v3 (Current)",
            doc_type="policy",
            status="current",
            page_count=1,
        ),
        full_text="ParcelPilot Support Policy v3. Section 4.1 Cancellation Policy: Enterprise customers may request cancellation without fee.",
        pages=[
            PageContent(
                page_number=1,
                text="ParcelPilot Support Policy v3. Section 4.1 Cancellation Policy: Enterprise customers may request cancellation without fee."
            )
        ]
    )

    chunks = chunk_document(sample_doc, chunk_size=50, overlap=10)
    assert len(chunks) > 0
    first_chunk = chunks[0]
    meta = first_chunk.metadata
    assert meta["document_filename"] == "01_Support_Policy_v3_CURRENT.pdf"
    assert meta["document_title"] == "Support Policy v3 (Current)"
    assert meta["document_type"] == "policy"
    assert meta["status"] == "current"
    assert meta["page_number"] == 1
    assert meta["authority"] == "general_policy"
    assert "chunk_index" in meta


def test_vector_store_and_semantic_retrieval(tmp_path):
    """Test ChromaDB vector store insertion and semantic search retrieval."""
    test_db_dir = tmp_path / "chroma_test"
    vsm = VectorStoreManager(persist_directory=str(test_db_dir), collection_name="test_collection")
    vsm.reset_collection()

    sample_doc = ParsedDocument(
        metadata=DocumentMetadata(
            filename="05_Northstar_Agreement.pdf",
            title="Northstar Agreement",
            doc_type="customer_agreement",
            status="current",
            customer="Northstar Logistics",
            page_count=1,
        ),
        full_text="Northstar Logistics Enterprise Agreement: Section 12.3 cancellation fee waiver applies if cancelled 24 hours prior to pickup.",
        pages=[
            PageContent(
                page_number=1,
                text="Northstar Logistics Enterprise Agreement: Section 12.3 cancellation fee waiver applies if cancelled 24 hours prior to pickup."
            )
        ]
    )

    chunks = chunk_document(sample_doc)
    vsm.add_chunks(chunks)

    retriever = CustomerAwareRetriever(vector_store=vsm)
    res = retriever.retrieve(query="cancellation fee waiver", customer="Northstar Logistics")

    assert res.total_results > 0
    top_hit = res.results[0]
    assert "cancellation" in top_hit.text.lower()
    assert top_hit.metadata["authority"] == "customer_agreement"
    assert top_hit.metadata["customer"] == "Northstar Logistics"


def test_customer_specific_filtering(tmp_path):
    """Test metadata filtering prioritizes or restricts retrieval by customer name."""
    test_db_dir = tmp_path / "chroma_filter_test"
    vsm = VectorStoreManager(persist_directory=str(test_db_dir), collection_name="filter_test")
    vsm.reset_collection()

    doc_northstar = ParsedDocument(
        metadata=DocumentMetadata(
            filename="05_Northstar.pdf",
            title="Northstar Agreement",
            doc_type="customer_agreement",
            status="current",
            customer="Northstar Logistics",
            page_count=1,
        ),
        full_text="Northstar specific cancellation terms.",
        pages=[PageContent(page_number=1, text="Northstar specific cancellation terms.")]
    )

    doc_lumen = ParsedDocument(
        metadata=DocumentMetadata(
            filename="06_LumenWorks.pdf",
            title="LumenWorks Agreement",
            doc_type="customer_agreement",
            status="current",
            customer="LumenWorks",
            page_count=1,
        ),
        full_text="LumenWorks specific cancellation terms.",
        pages=[PageContent(page_number=1, text="LumenWorks specific cancellation terms.")]
    )

    vsm.add_chunks(chunk_document(doc_northstar))
    vsm.add_chunks(chunk_document(doc_lumen))

    retriever = CustomerAwareRetriever(vector_store=vsm)
    
    # Retrieve with Northstar filter
    res = retriever.retrieve(query="cancellation terms", customer="Northstar Logistics")
    for r in res.results:
        assert r.metadata["customer"] in ["Northstar Logistics", ""]


def test_semantic_search_api():
    """Test GET /search API endpoint."""
    res = client.get("/search?q=cancellation")
    assert res.status_code == 200
    data = res.json()
    assert "query" in data
    assert "results" in data
    assert isinstance(data["results"], list)
