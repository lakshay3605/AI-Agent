"""PDF Document Parser using PyMuPDF (fitz)."""

import os
import logging
from pathlib import Path
from typing import List, Tuple
import fitz  # PyMuPDF

from app.models.document import ParsedDocument, DocumentMetadata, PageContent

logger = logging.getLogger("parcelpilot.pdf_parser")


def classify_document(filename: str, full_text: str) -> Tuple[str, str, str, str]:
    """
    Classify a document based on filename and extracted text.
    
    Returns:
        Tuple of (title, doc_type, status, customer_name)
    """
    lower_fn = filename.lower()
    lower_text = full_text.lower()

    # Default values
    doc_type = "policy"
    status = "current"
    customer = None
    title = filename.replace("_", " ").replace(".pdf", "")

    # Classify based on filename patterns & text markers
    if "deprecated" in lower_fn or "v2" in lower_fn:
        status = "deprecated"
    
    if "support_policy" in lower_fn or "support policy" in lower_fn:
        doc_type = "policy"
        if "v3" in lower_fn or "current" in lower_fn:
            title = "Support Policy v3 (Current)"
            status = "current"
        elif "v2" in lower_fn or "deprecated" in lower_fn:
            title = "Support Policy v2 (Deprecated)"
            status = "deprecated"
    elif "sop" in lower_fn or "cancellation" in lower_fn:
        doc_type = "sop"
        title = "Cancellation & Service Credit SOP v4"
    elif "operations_guide" in lower_fn or "known_issues" in lower_fn or "product" in lower_fn:
        doc_type = "operations_guide"
        title = "Product Operations Guide & Known Issues"
    elif "northstar" in lower_fn:
        doc_type = "customer_agreement"
        title = "Northstar Logistics Enterprise Agreement"
        customer = "Northstar Logistics"
    elif "lumenworks" in lower_fn:
        doc_type = "customer_agreement"
        title = "LumenWorks Service Agreement"
        customer = "LumenWorks"

    # Secondary text inspect for customer name if not found in filename
    if not customer:
        if "northstar logistics" in lower_text:
            customer = "Northstar Logistics"
        elif "lumenworks" in lower_text:
            customer = "LumenWorks"

    return title, doc_type, status, customer


def parse_pdf_file(file_path: Path) -> ParsedDocument:
    """Parse a single PDF file using PyMuPDF and extract pages and metadata."""
    filename = file_path.name
    pages: List[PageContent] = []
    full_text_chunks: List[str] = []

    try:
        doc = fitz.open(str(file_path))
        page_count = len(doc)

        for page_idx in range(page_count):
            page = doc.load_page(page_idx)
            text = page.get_text("text") or ""
            text = text.strip()
            pages.append(PageContent(page_number=page_idx + 1, text=text))
            if text:
                full_text_chunks.append(text)

        doc.close()
        full_text = "\n\n".join(full_text_chunks)
    except Exception as e:
        logger.error(f"Error parsing PDF file {file_path}: {e}")
        page_count = 0
        full_text = ""

    title, doc_type, status, customer = classify_document(filename, full_text)

    metadata = DocumentMetadata(
        filename=filename,
        title=title,
        doc_type=doc_type,
        status=status,
        customer=customer,
        page_count=page_count,
    )

    return ParsedDocument(
        metadata=metadata,
        full_text=full_text,
        pages=pages,
    )


def parse_all_pdfs(directory: Path) -> List[ParsedDocument]:
    """Scan directory for all PDF files and parse them into structured documents."""
    parsed_docs: List[ParsedDocument] = []
    if not directory.exists():
        logger.warning(f"Data directory {directory} does not exist.")
        return parsed_docs

    pdf_files = sorted(list(directory.glob("*.pdf")))
    logger.info(f"Found {len(pdf_files)} PDF files in {directory}")

    for pdf_path in pdf_files:
        doc = parse_pdf_file(pdf_path)
        parsed_docs.append(doc)

    return parsed_docs
