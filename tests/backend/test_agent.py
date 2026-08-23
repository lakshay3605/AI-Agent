"""Comprehensive Unit & Integration Tests for LangGraph AI Agent & Tool Execution Engine."""

import os
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.agent.graph import run_agent
from app.agent.security import validate_access, SecurityError
from app.agent.actions import (
    register_pending_action,
    get_pending_action,
    confirm_action,
    reject_action,
    clear_actions_store
)
from app.agent.tools import (
    tool_get_order,
    tool_get_customer,
    tool_get_ticket,
    tool_search_documents,
    tool_calculate_service_credit,
    tool_create_escalation
)

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_store():
    """Reset action store before each test run."""
    clear_actions_store()


def test_basic_document_question():
    """Test standard document RAG question answering."""
    res = run_agent(message="What is the general cancellation policy?")
    assert res["status"] in ["ANSWERED", "NEEDS_CLARIFICATION"]
    assert "response" in res
    assert len(res["response"]) > 0
    assert any("Searched knowledge base" in act for act in res["activity"])


def test_order_lookup():
    """Test order lookup tool invocation."""
    res = run_agent(message="Lookup order ORD-1001 details")
    assert any("ORD-1001" in act for act in res["activity"])
    assert "ORD-1001" in res["response"]


def test_customer_lookup():
    """Test customer lookup tool invocation."""
    res = run_agent(message="Show customer account details for Northstar Logistics")
    assert any("Northstar Logistics" in act for act in res["activity"])
    assert "Northstar" in res["response"]


def test_ticket_lookup():
    """Test ticket lookup tool invocation."""
    res = run_agent(message="What is status of support ticket TKT-501?")
    assert any("TKT-501" in act for act in res["activity"])
    assert "TKT-501" in res["response"]


def test_multistep_question():
    """Test multi-step question (Order lookup + Customer agreement + Policy calculation)."""
    res = run_agent(message="Can Northstar Logistics cancel order ORD-1001 without a fee?")
    assert any("ORD-1001" in act for act in res["activity"])
    assert any("Northstar Logistics" in act for act in res["activity"])
    assert "response" in res
    assert len(res["sources"]) > 0


def test_customer_agreement_vs_general_policy():
    """Test customer agreement precedence over general policy."""
    res = run_agent(message="What are credit terms for Northstar Logistics under Enterprise Agreement?")
    assert any("Northstar" in act for act in res["activity"])
    assert any(s.get("authority") == "customer_agreement" for s in res["sources"])


def test_deprecated_policy_handling():
    """Test deprecated policy awareness."""
    res = run_agent(message="Search support SLA response times in deprecated policy v2")
    assert len(res["sources"]) > 0
    # Deprecated document retrieved but flagged
    has_deprecated = any(s.get("status") == "deprecated" for s in res["sources"])
    assert has_deprecated or "DEPRECATED" in res["response"]


def test_missing_information_handling():
    """Test missing information handling for service credit calculation."""
    res = tool_calculate_service_credit(
        order_id="ORD-1001",
        user_context={"user_id": "usr_test", "role": "support_agent"}
    )
    # Checks structured status
    assert "status" in res
    assert res["status"] in ["CALCULATED", "NEEDS_CLARIFICATION"]


def test_unauthorized_access_security():
    """Test security model restricting user to assigned account scope."""
    restricted_context = {"user_id": "usr_restricted", "role": "support_agent", "account_scope": "Northstar Logistics"}
    
    # Accessing Northstar data should succeed
    validate_access(restricted_context, "Northstar Logistics")

    # Accessing LumenWorks data must raise SecurityError
    with pytest.raises(SecurityError):
        validate_access(restricted_context, "LumenWorks")

    # Test agent response under restricted context
    agent_res = run_agent(
        message="Show details for LumenWorks order ORD-2001",
        user_context=restricted_context
    )
    assert agent_res["status"] == "NEEDS_HUMAN_REVIEW"
    assert "Unauthorized" in agent_res["response"] or "Security" in agent_res["response"]


def test_action_preparation():
    """Test state-changing action tool creates pending confirmation."""
    res = run_agent(message="Please escalate support ticket TKT-501 to engineering")
    assert res["status"] == "ACTION_PENDING_CONFIRMATION"
    assert res["pending_action"] is not None
    assert res["pending_action"]["status"] == "pending_confirmation"
    assert res["pending_action"]["ticket_id"] == "TKT-501"


def test_action_confirmation_endpoint():
    """Test API endpoint confirming pending action."""
    action = register_pending_action(
        action_type="create_escalation",
        summary="Escalate ticket TKT-501",
        reason="Persistent shipment creation failure",
        customer="Northstar Logistics",
        ticket_id="TKT-501"
    )

    resp = client.post(f"/api/v1/actions/{action.action_id}/confirm")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "confirmed"
    assert data["result"]["executed"] is True


def test_action_rejection_endpoint():
    """Test API endpoint rejecting pending action."""
    action = register_pending_action(
        action_type="create_escalation",
        summary="Escalate ticket TKT-502",
        reason="Bulk CSV upload issue",
        customer="Northstar Logistics",
        ticket_id="TKT-502"
    )

    resp = client.post(f"/api/v1/actions/{action.action_id}/reject")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "rejected"
    assert data["result"]["executed"] is False


def test_agent_chat_api_endpoint():
    """Test full FastAPI POST /api/v1/agent/chat endpoint."""
    payload = {
        "message": "What is the cancellation SOP for ParcelPilot?",
        "conversation_id": "test_conv_99",
        "user_context": {"user_id": "test_user", "role": "support_agent"}
    }
    resp = client.post("/api/v1/agent/chat", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "response" in data
    assert "status" in data
    assert isinstance(data["activity"], list)
    assert isinstance(data["sources"], list)


def test_llm_config_error_when_key_missing(monkeypatch):
    """Verify that get_chat_model raises LLMConfigError if GEMINI_API_KEY is not set."""
    from app.llm import get_chat_model, LLMConfigError, clear_llm_cache
    clear_llm_cache()
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(LLMConfigError):
        get_chat_model(api_key="")


def test_gemini_failure_does_not_use_deterministic_fallback(monkeypatch):
    """Gemini failures must be surfaced instead of replaced with a fabricated answer."""
    from app.agent import nodes
    from app.llm import LLMConfigError

    def raise_config_error():
        raise LLMConfigError("Gemini is unavailable")

    monkeypatch.setattr(nodes, "get_chat_model", raise_config_error)
    with pytest.raises(LLMConfigError, match="Gemini is unavailable"):
        nodes.call_llm_node({"messages": [{"role": "user", "content": "Lookup ORD-1001"}]})


@pytest.mark.skipif(
    os.getenv("RUN_LLM_INTEGRATION_TESTS") != "true",
    reason="RUN_LLM_INTEGRATION_TESTS is not enabled"
)
def test_real_llm_tool_calling_integration():
    """Optional integration test executing real Chat LLM tool calling when enabled."""
    res = run_agent(message="Can Northstar Logistics cancel order ORD-1001 without a fee under their enterprise agreement?")
    assert "response" in res
    assert len(res["response"]) > 0
    assert any("ORD-1001" in act for act in res["activity"])
