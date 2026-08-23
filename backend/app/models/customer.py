"""Customer data model."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class Customer(BaseModel):
    """Customer account record."""
    customer_name: str = Field(..., description="Customer / Account name (e.g. Northstar Logistics)")
    tier: Optional[str] = Field(default="Enterprise", description="Account tier (Enterprise, Standard, Preferred)")
    agreement_type: Optional[str] = Field(default="Enterprise Agreement", description="Contract agreement type")
    total_orders: int = Field(default=0, description="Total order volume")
    active_tickets: List[str] = Field(default_factory=list, description="Active ticket IDs")
    contact_email: Optional[str] = Field(default=None, description="Account contact email")
    extra_attributes: Dict[str, Any] = Field(default_factory=dict, description="Additional customer properties")
