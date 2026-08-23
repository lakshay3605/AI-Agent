"""Unit tests for Backend Data Layer (authentic file parsing & API endpoints)."""

import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    """Test /health endpoint."""
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"


def test_root():
    """Test / root endpoint."""
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "online"
    assert "health" in data


def test_get_documents():
    """Test GET /documents endpoint."""
    res = client.get("/documents")
    assert res.status_code == 200
    docs = res.json()
    assert isinstance(docs, list)


def test_get_orders_list():
    """Test GET /orders endpoint."""
    res = client.get("/orders")
    assert res.status_code == 200
    orders = res.json()
    assert isinstance(orders, list)


def test_get_customers_list():
    """Test GET /customers endpoint."""
    res = client.get("/customers")
    assert res.status_code == 200
    custs = res.json()
    assert isinstance(custs, list)


def test_get_tickets_list():
    """Test GET /tickets endpoint."""
    res = client.get("/tickets")
    assert res.status_code == 200
    tickets = res.json()
    assert isinstance(tickets, list)
