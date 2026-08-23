"""FastAPI Pending Action Confirmation and Rejection Endpoints."""

import logging
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.agent.actions import (
    confirm_action,
    reject_action,
    get_pending_action,
    list_pending_actions,
    PendingAction
)

logger = logging.getLogger("parcelpilot.api.actions")

router = APIRouter()


class ActionConfirmationRequest(BaseModel):
    user_context: Optional[Dict[str, Any]] = Field(
        default_factory=lambda: {"user_id": "usr_default", "role": "support_agent"},
        description="User context performing confirmation or rejection"
    )


@router.get("/actions/pending", response_model=List[PendingAction])
def get_all_pending_actions():
    """List all registered pending actions."""
    return list_pending_actions()


@router.post("/actions/{action_id}/confirm", response_model=PendingAction)
def confirm_pending_action(action_id: str, payload: Optional[ActionConfirmationRequest] = None):
    """
    Human executive confirms pending state-changing action for backend execution.
    """
    user_ctx = payload.user_context if payload else {"user_id": "human_executive", "role": "support_agent"}
    try:
        updated_action = confirm_action(action_id=action_id, user_context=user_ctx)
        return updated_action
    except ValueError as val_err:
        raise HTTPException(status_code=404, detail=str(val_err))
    except Exception as e:
        logger.error(f"Error confirming action '{action_id}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to confirm action: {str(e)}")


@router.post("/actions/{action_id}/reject", response_model=PendingAction)
def reject_pending_action(action_id: str, payload: Optional[ActionConfirmationRequest] = None):
    """
    Human executive rejects pending state-changing action.
    """
    user_ctx = payload.user_context if payload else {"user_id": "human_executive", "role": "support_agent"}
    try:
        updated_action = reject_action(action_id=action_id, user_context=user_ctx)
        return updated_action
    except ValueError as val_err:
        raise HTTPException(status_code=404, detail=str(val_err))
    except Exception as e:
        logger.error(f"Error rejecting action '{action_id}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to reject action: {str(e)}")
