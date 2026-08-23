"""LangGraph Agent State definition."""

from typing import TypedDict, List, Dict, Any, Optional


class AgentState(TypedDict):
    """Shared state dictionary passed across LangGraph nodes."""
    messages: List[Dict[str, Any]]
    user_context: Dict[str, Any]
    conversation_id: str
    activity: List[str]
    sources: List[Dict[str, Any]]
    status: str  # ANSWERED, NEEDS_CLARIFICATION, NEEDS_HUMAN_REVIEW, ACTION_PENDING_CONFIRMATION, ACTION_COMPLETED
    pending_action: Optional[Dict[str, Any]]
    final_response: Optional[str]
