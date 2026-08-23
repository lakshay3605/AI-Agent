"""FastAPI Agent Chat Endpoint."""

import logging
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.agent.graph import run_agent

logger = logging.getLogger("parcelpilot.api.agent")

router = APIRouter()


class AgentChatRequest(BaseModel):
    message: str = Field(..., description="User query or instruction prompt")
    conversation_id: Optional[str] = Field(default="conv_default", description="Conversation session ID")
    user_context: Optional[Dict[str, Any]] = Field(
        default_factory=lambda: {"user_id": "usr_default", "role": "support_agent"},
        description="Security user context including role and account scope"
    )


class AgentChatResponse(BaseModel):
    response: str = Field(..., description="Grounded natural language response")
    status: str = Field(..., description="Status: ANSWERED, NEEDS_CLARIFICATION, NEEDS_HUMAN_REVIEW, ACTION_PENDING_CONFIRMATION, ACTION_COMPLETED")
    activity: List[str] = Field(default_factory=list, description="High-level non-confidential activity steps")
    sources: List[Dict[str, Any]] = Field(default_factory=list, description="Retrieved RAG source passages and metadata")
    pending_action: Optional[Dict[str, Any]] = Field(default=None, description="Action awaiting human confirmation if applicable")


@router.post("/agent/chat", response_model=AgentChatResponse)
def agent_chat(payload: AgentChatRequest):
    """
    Process human executive query through LangGraph Agent and tool execution engine.
    """
    if not payload.message.strip():
        raise HTTPException(status_code=400, detail="Message prompt cannot be empty.")

    try:
        result = run_agent(
            message=payload.message,
            conversation_id=payload.conversation_id,
            user_context=payload.user_context
        )
        return AgentChatResponse(**result)
    except Exception as e:
        logger.error(f"Error executing agent chat: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")
