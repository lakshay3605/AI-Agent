"""Customers API endpoints."""

from typing import List
from fastapi import APIRouter, HTTPException, Depends

from app.models.customer import Customer
from app.services.data_service import DataService, get_data_service

router = APIRouter()


@router.get("/customers/{customer_name}", response_model=Customer, summary="Get customer details")
async def get_customer(
    customer_name: str, 
    ds: DataService = Depends(get_data_service)
) -> Customer:
    """Retrieve customer account details by name (e.g. Northstar Logistics)."""
    customer = ds.get_customer(customer_name)
    if not customer:
        raise HTTPException(
            status_code=404, 
            detail=f"Customer '{customer_name}' not found."
        )
    return customer


@router.get("/customers", response_model=List[Customer], summary="List all customers")
async def list_customers(ds: DataService = Depends(get_data_service)) -> List[Customer]:
    """Retrieve list of all customer accounts."""
    return list(ds.customers.values())
