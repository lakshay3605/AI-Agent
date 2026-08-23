"""LangGraph StateGraph compilation for ParcelPilot AI Support Agent."""

import logging
from typing import Dict, Any, Optional

from langgraph.graph import StateGraph, END

from app.agent.state import AgentState
from app.agent.nodes import (
    call_llm_node,
    execute_tools_node,
    fallback_reasoning_node,
)

logger = logging.getLogger("parcelpilot.agent")

# Maximum number of tool-execution rounds allowed for one request.
MAX_TOOL_ROUNDS = 3


def _count_tool_rounds(state: AgentState) -> int:
    """Count completed tool execution rounds."""
    messages = state.get("messages", [])

    # Every ToolMessage represents a completed tool call.
    # We count them as a safety mechanism against infinite agent loops.
    return sum(
        1
        for message in messages
        if message.__class__.__name__ == "ToolMessage"
    )


def should_continue(state: AgentState) -> str:
    """
    Decide whether the graph should execute tools or finish.

    A hard tool-round limit prevents an LLM from getting stuck in
    an agent -> tools -> agent loop indefinitely.
    """
    messages = state.get("messages", [])
    status = state.get("status")

    if status in ["ACTION_PENDING_CONFIRMATION", "NEEDS_HUMAN_REVIEW"]:
        return "end"

    if not messages:
        return "end"

    last_message = messages[-1]
    tool_calls = getattr(last_message, "tool_calls", [])

    if not tool_calls or status != "IN_PROGRESS":
        return "end"

    tool_rounds = _count_tool_rounds(state)

    if tool_rounds >= MAX_TOOL_ROUNDS:
        logger.warning(
            "Maximum tool rounds reached (%s). Ending agent loop.",
            MAX_TOOL_ROUNDS,
        )
        return "fallback"

    return "tools"


def build_agent_graph():
    """Build and compile the LangGraph agent state graph."""
    workflow = StateGraph(AgentState)

    workflow.add_node("agent", call_llm_node)
    workflow.add_node("tools", execute_tools_node)
    workflow.add_node("fallback", fallback_reasoning_node)

    workflow.set_entry_point("agent")

    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "fallback": "fallback",
            "end": END,
        },
    )

    workflow.add_edge("tools", "agent")
    workflow.add_edge("fallback", END)

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
    user_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Run the LangGraph Agent pipeline for an incoming user message.
    """
    graph = get_agent_graph()

    initial_state: AgentState = {
        "messages": [{"role": "user", "content": message}],
        "user_context": user_context
        or {
            "user_id": "usr_default",
            "role": "support_agent",
        },
        "conversation_id": conversation_id,
        "activity": [],
        "sources": [],
        "status": "ANSWERED",
        "pending_action": None,
        "final_response": None,
    }

    try:
        result = graph.invoke(
            initial_state,
            config={"recursion_limit": 10},
        )

    except Exception as exc:
        logger.error(
            "Agent graph failed: %s",
            exc,
            exc_info=True,
        )

        # Last-resort deterministic fallback.
        # This keeps the API responsive even if the LLM/tool loop fails.
        result = fallback_reasoning_node(initial_state)

    # Format response text
    response_text = result.get("final_response")

    if not response_text and result.get("messages"):
        last_msg = result["messages"][-1]
        response_text = getattr(
            last_msg,
            "content",
            str(last_msg),
        )

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
        "pending_action": result.get("pending_action"),
    }