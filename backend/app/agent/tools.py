"""Real Tool Registry for ParcelPilot AI Agent."""

import logging
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

from app.services.data_service import get_data_service
from app.rag.retriever import CustomerAwareRetriever
from app.agent.security import validate_access, SecurityError
from app.agent.actions import register_pending_action, PendingAction

logger = logging.getLogger("parcelpilot.tools")


# --- Tool Result Schemas ---

class SearchDocumentsInput(BaseModel):
    query: str = Field(..., description="Semantic search query (e.g. cancellation policy, SLA terms)")
    customer_name: Optional[str] = Field(default=None, description="Optional customer name to scope search")
    top_k: int = Field(default=5, description="Number of results to retrieve")


class GetOrderInput(BaseModel):
    order_id: str = Field(..., description="Order ID (e.g. ORD-1001)")


class GetCustomerInput(BaseModel):
    customer_name: str = Field(..., description="Customer or Account name (e.g. Northstar Logistics)")


class GetTicketInput(BaseModel):
    ticket_id: str = Field(..., description="Ticket ID (e.g. TKT-501 or T-102)")


class CalculateServiceCreditInput(BaseModel):
    order_id: str = Field(..., description="Order ID to calculate SLA service credit for")


class CreateEscalationInput(BaseModel):
    ticket_id: str = Field(..., description="Ticket ID to prepare escalation for")
    reason: str = Field(..., description="Reason for escalation")
    priority: str = Field(default="high", description="Priority level: low, medium, high, urgent")


# --- Tool Implementations ---

def tool_search_documents(
    query: str, 
    customer_name: Optional[str] = None, 
    top_k: int = 5,
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Search RAG vector database for relevant policy, SOP, or contract passages.
    """
    if customer_name:
        validate_access(user_context, customer_name)

    retriever = CustomerAwareRetriever()
    response = retriever.retrieve(query=query, customer=customer_name, limit=top_k)

    results = []
    for r in response.results:
        results.append({
            "text": r.text,
            "document": r.metadata.get("document_name", r.document),
            "page": r.page,
            "score": r.score,
            "authority": r.metadata.get("authority", "general"),
            "status": r.metadata.get("status", "current"),
            "customer": r.metadata.get("customer", None),
            "document_type": r.metadata.get("type", "policy")
        })

    logger.info(f"Tool search_documents executed: query='{query}', returned {len(results)} chunks.")
    return {
        "query": query,
        "customer": customer_name,
        "count": len(results),
        "results": results,
        "activity": f"✓ Searched knowledge base for '{query}'"
    }


def tool_get_order(order_id: str, user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Retrieve operational order details by Order ID.
    """
    ds = get_data_service()
    order = ds.get_order(order_id)
    if not order:
        return {
            "found": False,
            "order_id": order_id,
            "message": f"Order '{order_id}' not found in operational database.",
            "activity": f"✓ Looked up order {order_id} (Not Found)"
        }

    validate_access(user_context, order.customer)

    return {
        "found": True,
        "order_id": order.order_id,
        "customer": order.customer,
        "carrier": order.carrier,
        "status": order.status,
        "pickup_date": order.pickup_date,
        "cancellation_fee_eligible": order.cancellation_fee_eligible,
        "extra_attributes": order.extra_attributes,
        "activity": f"✓ Looked up order {order.order_id}"
    }


def tool_get_customer(customer_name: str, user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Retrieve customer account record by customer name.
    """
    validate_access(user_context, customer_name)

    ds = get_data_service()
    cust = ds.get_customer(customer_name)
    if not cust:
        return {
            "found": False,
            "customer_name": customer_name,
            "message": f"Customer account '{customer_name}' not found.",
            "activity": f"✓ Retrieved customer record for '{customer_name}' (Not Found)"
        }

    return {
        "found": True,
        "customer_name": cust.customer_name,
        "tier": cust.tier,
        "agreement_type": cust.agreement_type,
        "total_orders": cust.total_orders,
        "active_tickets": cust.active_tickets,
        "extra_attributes": cust.extra_attributes,
        "activity": f"✓ Retrieved customer record for '{cust.customer_name}'"
    }


def tool_get_ticket(ticket_id: str, user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Retrieve support ticket record by ticket ID.
    """
    ds = get_data_service()
    tkt = ds.get_ticket(ticket_id)
    if not tkt:
        return {
            "found": False,
            "ticket_id": ticket_id,
            "message": f"Ticket '{ticket_id}' not found in support dataset.",
            "activity": f"✓ Looked up support ticket {ticket_id} (Not Found)"
        }

    validate_access(user_context, tkt.customer)

    return {
        "found": True,
        "ticket_id": tkt.ticket_id,
        "customer": tkt.customer,
        "account_id": tkt.extra_attributes.get("account_id", "N/A"),
        "issue_type": tkt.issue_type,
        "status": tkt.status,
        "description": tkt.reason or tkt.issue_type,
        "assigned_to": tkt.extra_attributes.get("assigned_to", "Unassigned"),
        "extra_attributes": tkt.extra_attributes,
        "activity": f"✓ Looked up support ticket {tkt.ticket_id}"
    }


def tool_calculate_service_credit(order_id: str, user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Calculate SLA service credit based ONLY on authentic order records and contract terms.
    Does NOT hallucinate missing input data.
    """
    ds = get_data_service()
    order = ds.get_order(order_id)
    if not order:
        return {
            "status": "NEEDS_CLARIFICATION",
            "eligible": False,
            "reason": f"Order '{order_id}' was not found in operational data.",
            "activity": f"✓ Calculated service credit for {order_id} (Order Not Found)"
        }

    validate_access(user_context, order.customer)

    extras = order.extra_attributes or {}
    carrier_fault = extras.get("carrier_fault")
    customer_fault = extras.get("customer_fault")
    shipment_fee = extras.get("shipment_fee_inr", 0.0)

    # Missing information check
    if carrier_fault is None or customer_fault is None:
        return {
            "status": "NEEDS_CLARIFICATION",
            "eligible": False,
            "order_id": order.order_id,
            "customer": order.customer,
            "reason": f"Insufficient fault attribution data for order '{order_id}'. Carrier fault or customer fault is unrecorded.",
            "missing_fields": ["carrier_fault" if carrier_fault is None else None, "customer_fault" if customer_fault is None else None],
            "activity": f"✓ Attempted service credit calculation for {order_id} (Missing Fault Data)"
        }

    # Evaluate eligibility based on policy: Carrier fault must be True and Customer fault False
    is_carrier_fault = str(carrier_fault).strip().upper() in ["TRUE", "1", "YES"]
    is_customer_fault = str(customer_fault).strip().upper() in ["TRUE", "1", "YES"]

    if not is_carrier_fault or is_customer_fault:
        return {
            "status": "CALCULATED",
            "eligible": False,
            "credit_percentage": 0.0,
            "credit_amount_inr": 0.0,
            "order_id": order.order_id,
            "customer": order.customer,
            "reason": "Ineligible for credit: Carrier was not at fault or customer was at fault.",
            "activity": f"✓ Calculated service credit for {order.order_id} (Ineligible)"
        }

    # Retrieve customer tier / agreement terms
    cust = ds.get_customer(order.customer)
    credit_pct = 15.0 if (cust and cust.tier == "Enterprise") else 10.0
    credit_amount = (credit_pct / 100.0) * float(shipment_fee)

    return {
        "status": "CALCULATED",
        "eligible": True,
        "credit_percentage": credit_pct,
        "credit_amount_inr": credit_amount,
        "order_id": order.order_id,
        "customer": order.customer,
        "reason": f"Eligible for {credit_pct}% SLA credit due to verified carrier fault.",
        "activity": f"✓ Calculated service credit for {order.order_id} (INR {credit_amount})"
    }


def tool_create_escalation(
    ticket_id: str, 
    reason: str, 
    priority: str = "high",
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    STATE-CHANGING ACTION: Prepare ticket escalation for human confirmation.
    Does NOT modify live state directly. Creates a pending action.
    """
    ds = get_data_service()
    tkt = ds.get_ticket(ticket_id)
    customer_name = tkt.customer if tkt else "Unknown Customer"

    if tkt:
        validate_access(user_context, tkt.customer)

    summary = f"Escalate support ticket {ticket_id} to Tier-2 Engineering ({priority.upper()} priority)"

    action = register_pending_action(
        action_type="create_escalation",
        summary=summary,
        reason=reason,
        customer=customer_name,
        ticket_id=ticket_id,
        priority=priority
    )

    return {
        "status": "ACTION_PENDING_CONFIRMATION",
        "pending_action": action.model_dump(),
        "message": f"Escalation request for ticket '{ticket_id}' has been prepared and requires human confirmation.",
        "activity": f"✓ Prepared escalation request for ticket {ticket_id} (Pending Confirmation)"
    }


# --- LangChain Structured Tool Registrations for LLM Bindings ---

from langchain_core.tools import tool

@tool("search_documents", args_schema=SearchDocumentsInput)
def search_documents(query: str, customer_name: Optional[str] = None, top_k: int = 5) -> Dict[str, Any]:
    """Search RAG vector database for policy, SOP, operations, or customer agreement passages."""
    return tool_search_documents(query=query, customer_name=customer_name, top_k=top_k)

@tool("get_order", args_schema=GetOrderInput)
def get_order(order_id: str) -> Dict[str, Any]:
    """Retrieve operational order details by Order ID (e.g. ORD-1001)."""
    return tool_get_order(order_id=order_id)

@tool("get_customer", args_schema=GetCustomerInput)
def get_customer(customer_name: str) -> Dict[str, Any]:
    """Retrieve customer account details by customer name (e.g. Northstar Logistics)."""
    return tool_get_customer(customer_name=customer_name)

@tool("get_ticket", args_schema=GetTicketInput)
def get_ticket(ticket_id: str) -> Dict[str, Any]:
    """Retrieve support ticket details by ticket ID (e.g. TKT-501)."""
    return tool_get_ticket(ticket_id=ticket_id)

@tool("calculate_service_credit", args_schema=CalculateServiceCreditInput)
def calculate_service_credit(order_id: str) -> Dict[str, Any]:
    """Calculate SLA service credit based strictly on authentic order records and contract terms."""
    return tool_calculate_service_credit(order_id=order_id)

@tool("create_escalation", args_schema=CreateEscalationInput)
def create_escalation(ticket_id: str, reason: str, priority: str = "high") -> Dict[str, Any]:
    """STATE-CHANGING ACTION: Prepare ticket escalation for human confirmation. Does NOT modify state directly."""
    return tool_create_escalation(ticket_id=ticket_id, reason=reason, priority=priority)


# Exported list of tools for LLM binding
AGENT_TOOLS = [
    search_documents,
    get_order,
    get_customer,
    get_ticket,
    calculate_service_credit,
    create_escalation,
]

# Map tool name -> actual function execution
TOOL_MAP = {
    "search_documents": tool_search_documents,
    "get_order": tool_get_order,
    "get_customer": tool_get_customer,
    "get_ticket": tool_get_ticket,
    "calculate_service_credit": tool_calculate_service_credit,
    "create_escalation": tool_create_escalation,
}
