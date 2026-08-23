"""Order data model."""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class Order(BaseModel):
    """Order record from operational dataset."""
    order_id: str = Field(..., description="Unique order identifier (e.g. ORD-1001)")
    customer: str = Field(..., description="Customer / Account name")
    status: str = Field(..., description="Order status (Delivered, In Transit, Cancelled, Pending)")
    carrier: Optional[str] = Field(default=None, description="Carrier name (FedEx, UPS, DHL, Northstar Logistics)")
    tracking_number: Optional[str] = Field(default=None, description="Parcel tracking number")
    cancellation_fee_eligible: Optional[bool] = Field(default=None, description="Whether fee waiver applies")
    pickup_date: Optional[str] = Field(default=None, description="Scheduled or actual pickup timestamp")
    extra_attributes: Dict[str, Any] = Field(default_factory=dict, description="Additional sheet fields")
