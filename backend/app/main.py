"""FastAPI application entry point for ParcelPilot AI Agent Backend."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints import health, documents, orders, customers, tickets, search
from app.api.v1.router import api_router
from app.core.config import settings
from app.services.data_service import get_data_service


from app.rag.vector_store import VectorStoreManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifespan context manager."""
    # Pre-load data service on startup
    data_service = get_data_service()
    
    # Pre-warm embedding provider during container startup to avoid mid-request heap expansion
    try:
        vsm = VectorStoreManager()
        if hasattr(vsm.embedding_provider, "preload"):
            vsm.embedding_provider.preload()
    except Exception:
        pass

    yield


from fastapi import Request
from fastapi.responses import JSONResponse


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Backend data layer and RAG foundation for ParcelPilot AI Support Agent.",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler returning structured JSON errors."""
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred while processing your request.",
                "detail": str(exc) if settings.DEBUG else None
            }
        }
    )

# Configure CORS Middleware
if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Direct root-level endpoints as specified in Step 3
app.include_router(health.router, tags=["Health"])
app.include_router(documents.router, tags=["Documents"])
app.include_router(orders.router, tags=["Orders"])
app.include_router(customers.router, tags=["Customers"])
app.include_router(tickets.router, tags=["Tickets"])
app.include_router(search.router, tags=["Search"])

# Versioned API routes (/api/v1)
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint returning basic service info and API list."""
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "health": "/health",
        "endpoints": {
            "health": "/health",
            "documents": "/documents",
            "orders": "/orders/ORD-1001",
            "customers": "/customers/Northstar%20Logistics",
            "tickets": "/tickets/T-102",
            "search": "/search?q=cancellation",
            "docs": "/docs",
        },
    }
