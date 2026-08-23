"""Support ticket data model."""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class Ticket(BaseModel):
    """Support ticket record."""
    ticket_id: str = Field(..., description="Unique ticket identifier (e.g. T-102)")
    order_id: Optional[str] = Field(default=None, description="Associated order ID")
    customer: str = Field(..., description="Associated customer account")
    issue_type: str = Field(..., description="Issue categorization (Pickup Cancellation, SLA Delay, Loss)")
    priority: str = Field(default="Medium", description="High | Medium | Low")
    status: str = Field(default="Open", description="Open | Escalated | Resolved | Closed")
    created_at: str = Field(..., description="Creation date / timestamp")
    reason: Optional[str] = Field(default=None, description="Escalation or ticket detail reason")
    extra_attributes: Dict[str, Any] = Field(default_factory=dict, description="Additional ticket properties")
