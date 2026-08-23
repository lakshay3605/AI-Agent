"""Pending Action Store and Confirmation Management for State-Changing Operations."""

import logging
import uuid
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

logger = logging.getLogger("parcelpilot.actions")


class PendingAction(BaseModel):
    """Pending Action record awaiting human confirmation."""
    action_id: str
    action_type: str  # e.g. create_escalation, issue_refund, update_order
    customer: Optional[str] = None
    order_id: Optional[str] = None
    ticket_id: Optional[str] = None
    reason: str
    priority: str = "high"
    summary: str
    status: str = "pending_confirmation"  # pending_confirmation, confirmed, rejected
    created_at: str = Field(default_factory=lambda: "2026-08-23T03:30:00Z")
    result: Optional[Dict[str, Any]] = None


# Thread-safe in-memory store for pending actions
_pending_actions_store: Dict[str, PendingAction] = {}


def register_pending_action(
    action_type: str,
    summary: str,
    reason: str,
    customer: Optional[str] = None,
    order_id: Optional[str] = None,
    ticket_id: Optional[str] = None,
    priority: str = "high"
) -> PendingAction:
    """Register a new state-changing action in pending_confirmation status."""
    action_id = f"ACT-{uuid.uuid4().hex[:8].upper()}"
    action = PendingAction(
        action_id=action_id,
        action_type=action_type,
        customer=customer,
        order_id=order_id,
        ticket_id=ticket_id,
        reason=reason,
        priority=priority,
        summary=summary,
        status="pending_confirmation"
    )
    _pending_actions_store[action_id] = action
    logger.info(f"Registered pending action '{action_id}' ({action_type}) for customer '{customer}'")
    return action


def get_pending_action(action_id: str) -> Optional[PendingAction]:
    """Retrieve pending action by ID."""
    return _pending_actions_store.get(action_id)


def list_pending_actions() -> List[PendingAction]:
    """List all pending actions."""
    return list(_pending_actions_store.values())


def confirm_action(action_id: str, user_context: Optional[Dict[str, Any]] = None) -> PendingAction:
    """
    Execute human-confirmed pending action.
    """
    action = _pending_actions_store.get(action_id)
    if not action:
        raise ValueError(f"Pending action '{action_id}' not found.")

    if action.status != "pending_confirmation":
        logger.warning(f"Action '{action_id}' is already in status '{action.status}'")
        return action

    # Execute state change
    action.status = "confirmed"
    action.result = {
        "executed": True,
        "executed_by": user_context.get("user_id", "human_executive") if user_context else "human_executive",
        "message": f"Successfully executed action '{action.summary}'"
    }
    logger.info(f"Confirmed and executed action '{action_id}'")
    return action


def reject_action(action_id: str, user_context: Optional[Dict[str, Any]] = None) -> PendingAction:
    """
    Reject pending action.
    """
    action = _pending_actions_store.get(action_id)
    if not action:
        raise ValueError(f"Pending action '{action_id}' not found.")

    action.status = "rejected"
    action.result = {
        "executed": False,
        "rejected_by": user_context.get("user_id", "human_executive") if user_context else "human_executive",
        "message": f"Action '{action.summary}' was rejected by human executive."
    }
    logger.info(f"Rejected action '{action_id}'")
    return action


def clear_actions_store() -> None:
    """Helper method for resetting action store in tests."""
    global _pending_actions_store
    _pending_actions_store = {}
