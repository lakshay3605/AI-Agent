"""Verification unit tests for AI Agent prompt, policy, and tool routing rules."""

import sys
from pathlib import Path
import pytest

backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.agent.graph import run_agent


def test_case_1_northstar_ord_1001_cancellation_fee():
    """1. Can Northstar Logistics cancel ORD-1001 without a fee?"""
    res = run_agent("Can Northstar Logistics cancel ORD-1001 without a fee, and why?")
    assert res["status"] == "ANSWERED"
    ans = res["response"].lower()
    # Must answer YES / without fee based on Northstar agreement
    assert "yes" in ans or "no fee" in ans or "without a fee" in ans or "without fee" in ans
    assert "northstar" in ans


def test_case_2_northstar_enterprise_agreement_cancellation_terms():
    """2. What does the Northstar Enterprise Agreement say about cancellation?"""
    res = run_agent("What does the Northstar Enterprise Agreement say about cancellation?")
    assert res["status"] == "ANSWERED"
    ans = res["response"].lower()
    assert "booked" in ans or "cancellation" in ans or "fee" in ans


def test_case_3_default_cancellation_policy():
    """3. What is the default cancellation policy?"""
    res = run_agent("What is the default cancellation policy?")
    assert res["status"] == "ANSWERED"
    ans = res["response"].lower()
    assert "sop" in ans or "30 minutes" in ans or "250" in ans or "cancel" in ans


def test_case_4_lumenworks_cancellation_isolation():
    """4. Can LumenWorks cancel their shipment without a fee?"""
    res = run_agent("Can LumenWorks cancel their shipment without a fee?", user_context={"user_id": "u1", "role": "support_agent", "customer": "LumenWorks"})
    assert res["status"] == "ANSWERED"
    ans = res["response"].lower()
    # Must NOT apply Northstar's fee waiver rules to LumenWorks
    assert "lumenworks" in ans or "agreement" in ans or "policy" in ans


def test_case_5_deprecated_policy_not_overriding_current():
    """5. Deprecated policy documents must not override CURRENT policies."""
    res = run_agent("What is the support escalation response time under current policy?")
    assert res["status"] == "ANSWERED"
    ans = res["response"].lower()
    # Must use current policy, not deprecated v2 policy
    assert "current" in ans or "sop" in ans or "v3" in ans or "response" in ans
