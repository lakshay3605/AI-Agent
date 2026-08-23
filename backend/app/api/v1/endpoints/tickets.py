"""Tickets API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query

from app.models.ticket import Ticket
from app.services.data_service import DataService, get_data_service

router = APIRouter()


@router.get("/tickets/{ticket_id}", response_model=Ticket, summary="Get ticket by ID")
async def get_ticket(
    ticket_id: str, 
    ds: DataService = Depends(get_data_service)
) -> Ticket:
    """Retrieve support ticket details by ticket ID (e.g. T-102)."""
    ticket = ds.get_ticket(ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=404, 
            detail=f"Ticket '{ticket_id}' not found."
        )
    return ticket


@router.get("/tickets", response_model=List[Ticket], summary="Search or list tickets")
async def search_tickets(
    query: Optional[str] = Query(default=None, description="Search query across tickets"),
    ds: DataService = Depends(get_data_service)
) -> List[Ticket]:
    """List or search support tickets."""
    if query:
        return ds.search_tickets(query)
    return list(ds.tickets.values())
