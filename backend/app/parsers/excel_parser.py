"""Excel Workbook Parser using pandas."""

import logging
from pathlib import Path
from typing import Dict, List, Any, Tuple
import pandas as pd

from app.models.order import Order
from app.models.customer import Customer
from app.models.ticket import Ticket

logger = logging.getLogger("parcelpilot.excel_parser")


def parse_excel_workbook(file_path: Path) -> Tuple[List[Order], List[Customer], List[Ticket], Dict[str, List[Dict[str, Any]]]]:
    """
    Parse an Excel workbook, auto-detecting all sheets and converting to DataFrames and entities.
    
    Returns:
        Tuple of (orders_list, customers_list, tickets_list, raw_sheets_dict)
    """
    orders: List[Order] = []
    customers: List[Customer] = []
    tickets: List[Ticket] = []
    raw_sheets: Dict[str, List[Dict[str, Any]]] = {}

    if not file_path.exists():
        logger.warning(f"Excel workbook {file_path} not found.")
        return orders, customers, tickets, raw_sheets

    try:
        excel_file = pd.ExcelFile(str(file_path))
        sheet_names = excel_file.sheet_names
        logger.info(f"Auto-detected {len(sheet_names)} sheets in {file_path.name}: {sheet_names}")

        for sheet in sheet_names:
            df = pd.read_excel(excel_file, sheet_name=sheet)
            # Fill NaN values with empty string or None for JSON serialization
            df = df.where(pd.notnull(df), None)
            records = df.to_dict(orient="records")
            raw_sheets[sheet] = records

            lower_sheet = sheet.lower()
            
            # Map sheet to domain entities based on column names or sheet name
            if "order" in lower_sheet or "shipment" in lower_sheet:
                for row in records:
                    order_obj = _map_order_row(row)
                    if order_obj:
                        orders.append(order_obj)

            elif "customer" in lower_sheet or "account" in lower_sheet or "client" in lower_sheet:
                for row in records:
                    cust_obj = _map_customer_row(row)
                    if cust_obj:
                        customers.append(cust_obj)

            elif "ticket" in lower_sheet or "issue" in lower_sheet or "support" in lower_sheet:
                for row in records:
                    ticket_obj = _map_ticket_row(row)
                    if ticket_obj:
                        tickets.append(ticket_obj)
            else:
                # Inspect columns if sheet name is ambiguous
                cols_str = " ".join([str(c).lower() for c in df.columns])
                if "order_id" in cols_str or "order id" in cols_str:
                    for row in records:
                        o = _map_order_row(row)
                        if o:
                            orders.append(o)
                elif "ticket_id" in cols_str or "ticket id" in cols_str:
                    for row in records:
                        t = _map_ticket_row(row)
                        if t:
                            tickets.append(t)

        excel_file.close()
    except Exception as e:
        logger.error(f"Error reading Excel workbook {file_path}: {e}")

    return orders, customers, tickets, raw_sheets


ACCOUNT_NAME_MAP = {
    "ACCT-001": "Northstar Logistics",
    "ACCT-002": "LumenWorks",
    "ACCT-003": "Beacon Retail",
    "ACCT-004": "Apex Global"
}


def _map_order_row(row: Dict[str, Any]) -> Order | None:
    """Safely map a raw row dictionary to an Order model."""
    order_id = _get_val(row, ["order_id", "order id", "id", "ord_id"])
    if not order_id:
        return None

    acct_id = _get_val(row, ["account_id", "account id", "account"])
    cust_name = ACCOUNT_NAME_MAP.get(str(acct_id).upper(), None) if acct_id else None
    if not cust_name:
        cust_name = _get_val(row, ["customer", "customer_name", "customer name"]) or "Unknown Customer"

    status = _get_val(row, ["status", "order_status", "state"]) or "Delivered"
    carrier = _get_val(row, ["carrier", "carrier_name", "courier"])
    tracking_number = _get_val(row, ["tracking_number", "tracking number", "tracking", "tracking_id"])
    
    fee_eligible_raw = _get_val(row, ["cancellation_fee_eligible", "fee_waived", "fee_waiver_eligible"])
    fee_eligible = True if str(fee_eligible_raw).lower() in ["true", "1", "yes"] else False if fee_eligible_raw is not None else None

    pickup_date = _get_val(row, ["pickup_date", "pickup date", "scheduled_pickup", "date"])

    return Order(
        order_id=str(order_id).strip(),
        customer=str(cust_name).strip(),
        status=str(status).strip(),
        carrier=str(carrier) if carrier else None,
        tracking_number=str(tracking_number) if tracking_number else None,
        cancellation_fee_eligible=fee_eligible,
        pickup_date=str(pickup_date) if pickup_date else None,
        extra_attributes=row,
    )


def _map_customer_row(row: Dict[str, Any]) -> Customer | None:
    """Safely map a raw row dictionary to a Customer model."""
    name = _get_val(row, ["account_name", "customer_name", "customer name", "customer", "company"])
    if not name:
        acct_id = _get_val(row, ["account_id", "account id"])
        if acct_id:
            name = ACCOUNT_NAME_MAP.get(str(acct_id).upper(), str(acct_id))
    if not name:
        return None

    tier = _get_val(row, ["tier", "account_tier", "plan"]) or "Enterprise"
    agreement = _get_val(row, ["agreement_type", "agreement", "contract"]) or "Enterprise Agreement"
    orders_cnt = _get_val(row, ["total_orders", "orders_count", "order_count"]) or 0

    return Customer(
        customer_name=str(name).strip(),
        tier=str(tier),
        agreement_type=str(agreement),
        total_orders=int(orders_cnt) if isinstance(orders_cnt, (int, float)) else 0,
        contact_email=_get_val(row, ["contact_email", "email"]),
        extra_attributes=row,
    )


def _map_ticket_row(row: Dict[str, Any]) -> Ticket | None:
    """Safely map a raw row dictionary to a Ticket model."""
    ticket_id = _get_val(row, ["ticket_id", "ticket id", "id", "t_id"])
    if not ticket_id:
        return None

    order_id = _get_val(row, ["order_id", "order id", "ord_id"])
    acct_id = _get_val(row, ["account_id", "account id", "account"])
    cust_name = ACCOUNT_NAME_MAP.get(str(acct_id).upper(), None) if acct_id else None
    if not cust_name:
        cust_name = _get_val(row, ["customer", "customer_name", "customer name"]) or "Northstar Logistics"

    issue_type = _get_val(row, ["issue_type", "issue type", "category", "subject"]) or "General Inquiry"
    priority = _get_val(row, ["priority", "level"]) or "Medium"
    status = _get_val(row, ["status", "state"]) or "Open"
    created_at = _get_val(row, ["created_at", "created at", "date", "created"]) or "2025-05-20"
    reason = _get_val(row, ["reason", "escalation_reason", "description"])

    return Ticket(
        ticket_id=str(ticket_id).strip(),
        order_id=str(order_id) if order_id else None,
        customer=str(cust_name).strip(),
        issue_type=str(issue_type).strip(),
        priority=str(priority).strip(),
        status=str(status).strip(),
        created_at=str(created_at).strip(),
        reason=str(reason) if reason else None,
        extra_attributes=row,
    )


import math

def _get_val(row: Dict[str, Any], keys: List[str]) -> Any:
    """Case-insensitive dictionary key lookup helper sanitizing pandas NaN values."""
    row_lower = {str(k).lower(): v for k, v in row.items()}
    for key in keys:
        if key in row_lower and row_lower[key] is not None:
            val = row_lower[key]
            if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
                continue
            if str(val).strip().lower() in ["nan", "none", "null"]:
                continue
            return val
    return None
