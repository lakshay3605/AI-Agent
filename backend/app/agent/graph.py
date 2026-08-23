"""LangGraph StateGraph compilation for ParcelPilot AI Support Agent."""

import logging
from typing import Dict, Any, Optional

from langgraph.graph import StateGraph, END
from app.agent.state import AgentState
from app.agent.nodes import call_llm_node, execute_tools_node

logger = logging.getLogger("parcelpilot.agent")


def should_continue(state: AgentState) -> str:
    """
    Router decision function evaluating whether the LLM produced tool calls
    or if execution is complete.
    """
    messages = state.get("messages", [])
    status = state.get("status")

    if status in ["ACTION_PENDING_CONFIRMATION", "NEEDS_HUMAN_REVIEW"]:
        return "end"

    if not messages:
        return "end"

    last_message = messages[-1]
    tool_calls = getattr(last_message, "tool_calls", [])

    if tool_calls and status == "IN_PROGRESS":
        return "tools"

    return "end"


def build_agent_graph():
    """Build and compile the LangGraph agent state graph."""
    workflow = StateGraph(AgentState)
    
    workflow.add_node("agent", call_llm_node)
    workflow.add_node("tools", execute_tools_node)

    workflow.set_entry_point("agent")

    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "end": END
        }
    )

    workflow.add_edge("tools", "agent")

    return workflow.compile()


# Global compiled agent graph instance
_agent_graph_instance = None


def get_agent_graph():
    """Accessor for singleton compiled LangGraph instance."""
    global _agent_graph_instance
    if _agent_graph_instance is None:
        _agent_graph_instance = build_agent_graph()
    return _agent_graph_instance


def run_agent(
    message: str, 
    conversation_id: str = "conv_default",
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Run the LangGraph Agent pipeline for an incoming user message.
    """
    graph = get_agent_graph()

    initial_state: AgentState = {
        "messages": [{"role": "user", "content": message}],
        "user_context": user_context or {"user_id": "usr_default", "role": "support_agent"},
        "conversation_id": conversation_id,
        "activity": [],
        "sources": [],
        "status": "ANSWERED",
        "pending_action": None,
        "final_response": None
    }

    result = graph.invoke(initial_state)

    # Format response text
    response_text = result.get("final_response")
    if not response_text and result.get("messages"):
        last_msg = result["messages"][-1]
        response_text = getattr(last_msg, "content", str(last_msg))

    if isinstance(response_text, list):
        text_blocks = [
            b.get("text", "") if isinstance(b, dict) else str(b)
            for b in response_text
            if not isinstance(b, dict) or b.get("type") == "text"
        ]
        response_text = "\n".join(text_blocks).strip()

    return {
        "response": response_text or "No response generated.",
        "status": result.get("status", "ANSWERED"),
        "activity": result.get("activity", []),
        "sources": result.get("sources", []),
        "pending_action": result.get("pending_action")
    }
