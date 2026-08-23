"""CLI Ingestion script to build/rebuild vector database index from PDFs."""

import logging
import sys
from pathlib import Path

# Add backend directory to sys.path if run directly
backend_dir = Path(__file__).resolve().parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.core.config import settings
from app.parsers.pdf_parser import parse_all_pdfs
from app.rag.chunker import chunk_document
from app.rag.vector_store import VectorStoreManager

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("parcelpilot.ingestion")


def run_ingestion(data_dir: Path = Path(settings.DATA_DIR), rebuild: bool = True) -> dict:
    """
    Run full document ingestion pipeline: Parse PDFs -> Chunk -> Embed -> Store in ChromaDB.
    """
    data_dir_path = Path(data_dir).resolve()
    print(f"\n==================================================")
    print(f"ParcelPilot RAG Ingestion Pipeline Starting")
    print(f"Data Directory: {data_dir_path}")
    print(f"==================================================\n")

    # 1. Parse PDFs
    parsed_docs = parse_all_pdfs(data_dir_path)
    total_docs = len(parsed_docs)
    total_pages = sum(d.metadata.page_count for d in parsed_docs)

    if total_docs == 0:
        print(f"Warning: No PDF files discovered in {data_dir_path}")
        return {"documents": 0, "pages": 0, "chunks": 0, "embedded": 0}

    # 2. Chunk Documents
    all_chunks = []
    for doc in parsed_docs:
        chunks = chunk_document(doc)
        all_chunks.extend(chunks)

    total_chunks = len(all_chunks)

    # 3. Store in Vector Database
    vector_store = VectorStoreManager()
    if rebuild:
        vector_store.reset_collection()

    embedded_count = vector_store.add_chunks(all_chunks)

    summary = {
        "documents": total_docs,
        "pages": total_pages,
        "chunks": total_chunks,
        "embedded": embedded_count,
    }

    print(f"\n--------------------------------------------------")
    print(f"Documents: {total_docs}")
    print(f"Pages:     {total_pages}")
    print(f"Chunks:    {total_chunks}")
    print(f"Embedded:  {embedded_count}")
    print(f"--------------------------------------------------")
    print(f"Vector index ready.\n")

    return summary


if __name__ == "__main__":
    run_ingestion()
