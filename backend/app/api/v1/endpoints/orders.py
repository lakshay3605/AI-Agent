"""Orders API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query

from app.models.order import Order
from app.services.data_service import DataService, get_data_service

router = APIRouter()


@router.get("/orders/{order_id}", response_model=Order, summary="Get order by ID")
async def get_order(
    order_id: str, 
    ds: DataService = Depends(get_data_service)
) -> Order:
    """Retrieve operational order details by order ID (e.g. ORD-1001)."""
    order = ds.get_order(order_id)
    if not order:
        raise HTTPException(
            status_code=404, 
            detail=f"Order '{order_id}' not found."
        )
    return order


@router.get("/orders", response_model=List[Order], summary="Search or list orders")
async def search_orders(
    query: Optional[str] = Query(default=None, description="Search query across orders"),
    ds: DataService = Depends(get_data_service)
) -> List[Order]:
    """List or search operational orders."""
    if query:
        return ds.search_orders(query)
    return list(ds.orders.values())
