"""Central DataService for in-memory caching and authentic data lookup API."""

import logging
from pathlib import Path
from typing import Dict, List, Optional
import re

from app.models.document import ParsedDocument, DocumentMetadata, PageContent
from app.models.order import Order
from app.models.customer import Customer
from app.models.ticket import Ticket
from app.models.search import SearchResponse, SearchResultItem
from app.parsers.pdf_parser import parse_all_pdfs
from app.parsers.excel_parser import parse_excel_workbook

logger = logging.getLogger("parcelpilot.data_service")


class DataService:
    """Central data service holding cached documents, orders, customers, and tickets from actual files."""

    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir).resolve()
        self.documents: Dict[str, ParsedDocument] = {}
        self.orders: Dict[str, Order] = {}
        self.customers: Dict[str, Customer] = {}
        self.tickets: Dict[str, Ticket] = {}
        self.raw_sheets: Dict[str, List[dict]] = {}
        self.is_loaded: bool = False

    def load_all_data(self) -> None:
        """Load and cache all PDF documents and Excel data from data_dir. NO hardcoded fallback seeds."""
        logger.info(f"Initializing DataService from directory: {self.data_dir.resolve()}")

        # 1. Parse PDFs
        pdf_docs = parse_all_pdfs(self.data_dir)
        for doc in pdf_docs:
            self.documents[doc.metadata.filename] = doc
            self.documents[doc.metadata.title] = doc

        # 2. Parse Excel Workbook
        excel_path = self.data_dir / "ParcelPilot_Assessment_Data.xlsx"
        if not excel_path.exists():
            matching = list(self.data_dir.glob("*.xlsx"))
            if matching:
                excel_path = matching[0]

        orders_list, cust_list, ticket_list, raw_sheets = parse_excel_workbook(excel_path)
        self.raw_sheets = raw_sheets

        for o in orders_list:
            self.orders[o.order_id.upper()] = o
        for c in cust_list:
            self.customers[c.customer_name.lower()] = c
        for t in ticket_list:
            self.tickets[t.ticket_id.upper()] = t

        self.is_loaded = True
        logger.info(
            f"DataService loaded authentic source data: {len(self.documents)} docs, {len(self.orders)} orders, "
            f"{len(self.customers)} customers, {len(self.tickets)} tickets."
        )

    # --- Helper Query API Methods ---

    def get_all_documents(self) -> List[DocumentMetadata]:
        """Return list of all indexed document metadata."""
        seen = set()
        result = []
        for doc in self.documents.values():
            if doc.metadata.filename not in seen:
                seen.add(doc.metadata.filename)
                result.append(doc.metadata)
        return result

    def get_document_by_name(self, name: str) -> Optional[ParsedDocument]:
        """Find single parsed document by filename or title match."""
        if name in self.documents:
            return self.documents[name]
        lower_name = name.lower()
        for doc in self.documents.values():
            if lower_name in doc.metadata.filename.lower() or lower_name in doc.metadata.title.lower():
                return doc
        return None

    def get_order(self, order_id: str) -> Optional[Order]:
        """Retrieve order by order ID (case-insensitive)."""
        return self.orders.get(order_id.upper().strip())

    def get_customer(self, customer_name: str) -> Optional[Customer]:
        """Retrieve customer details by customer name (case-insensitive)."""
        key = customer_name.lower().strip()
        if key in self.customers:
            return self.customers[key]
        for name, cust in self.customers.items():
            if key in name or name in key:
                return cust
        return None

    def get_ticket(self, ticket_id: str) -> Optional[Ticket]:
        """Retrieve support ticket by ticket ID (case-insensitive)."""
        return self.tickets.get(ticket_id.upper().strip())

    def search_orders(self, query: str) -> List[Order]:
        """Search orders matching query string across order ID, customer, status, or carrier."""
        q = query.lower().strip()
        results = []
        for o in self.orders.values():
            if (
                q in o.order_id.lower()
                or q in o.customer.lower()
                or q in o.status.lower()
                or (o.carrier and q in o.carrier.lower())
            ):
                results.append(o)
        return results

    def search_tickets(self, query: str) -> List[Ticket]:
        """Search tickets matching query string."""
        q = query.lower().strip()
        results = []
        for t in self.tickets.values():
            if (
                q in t.ticket_id.lower()
                or q in t.customer.lower()
                or q in t.issue_type.lower()
                or q in t.status.lower()
            ):
                results.append(t)
        return results


# Global singleton instance managed during FastAPI lifespan
_data_service_instance: Optional[DataService] = None


def get_data_service() -> DataService:
    """Dependency accessor for global DataService instance."""
    global _data_service_instance
    if _data_service_instance is None or not _data_service_instance.is_loaded:
        from app.core.config import settings
        _data_service_instance = DataService(data_dir=settings.DATA_DIR)
        _data_service_instance.load_all_data()
    return _data_service_instance
