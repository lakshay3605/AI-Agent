"""Main API Router for V1 endpoints."""

from fastapi import APIRouter
from app.api.v1.endpoints import health, documents, orders, customers, tickets, search, agent, actions

api_router = APIRouter()

# Include endpoint sub-routers
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(documents.router, tags=["Documents"])
api_router.include_router(orders.router, tags=["Orders"])
api_router.include_router(customers.router, tags=["Customers"])
api_router.include_router(tickets.router, tags=["Tickets"])
api_router.include_router(search.router, tags=["Search"])
api_router.include_router(agent.router, tags=["Agent"])
api_router.include_router(actions.router, tags=["Actions"])
