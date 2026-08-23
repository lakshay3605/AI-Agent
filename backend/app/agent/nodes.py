"""LangGraph Nodes for ParcelPilot AI Support Agent Reasoning Pipeline."""

import logging
import json
import re
from typing import Dict, Any, List
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage

from app.agent.state import AgentState
from app.agent.tools import (
    AGENT_TOOLS,
    TOOL_MAP,
    tool_search_documents,
    tool_get_order,
    tool_get_customer,
    tool_get_ticket,
    tool_calculate_service_credit,
    tool_create_escalation,
)
from app.agent.security import SecurityError
from app.agent.policies import resolve_policy_precedence
from app.agent.prompts import SYSTEM_PROMPT
from app.llm.client import get_chat_model, LLMConfigError

import math

logger = logging.getLogger("parcelpilot.nodes")


def sanitize_json_obj(obj: Any) -> Any:
    """Replace NaN / Inf float values with None for strict JSON compliance."""
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    elif isinstance(obj, dict):
        return {k: sanitize_json_obj(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_json_obj(x) for x in obj]
    return obj


def extract_entities(text: str) -> Dict[str, List[str]]:
    """Helper function to extract order IDs, ticket IDs, and customer names from prompt."""
    orders = re.findall(r"\bORD-\d+\b", text, re.IGNORECASE)
    tickets = re.findall(r"\b(?:TKT-\d+|T-\d+)\b", text, re.IGNORECASE)
    
    customers = []
    text_lower = text.lower()
    if "northstar" in text_lower:
        customers.append("Northstar Logistics")
    if "lumenworks" in text_lower or "lumen works" in text_lower:
        customers.append("LumenWorks")
    if "beacon" in text_lower:
        customers.append("Beacon Retail")
    if "apex" in text_lower:
        customers.append("Apex Global")

    return {
        "orders": [o.upper() for o in orders],
        "tickets": [t.upper() for t in tickets],
        "customers": customers
    }


def fallback_reasoning_node(state: AgentState) -> Dict[str, Any]:
    """
    Fallback rule-based reasoning engine used when LLM API key is missing or offline,
    ensuring standard unit tests pass without requiring a paid LLM key.
    """
    messages = state.get("messages", [])
    user_context = state.get("user_context", {})
    
    if not messages:
        return {
            "status": "NEEDS_CLARIFICATION",
            "final_response": "No prompt received.",
            "activity": [],
            "sources": []
        }

    latest_msg = messages[-1].get("content", "") if isinstance(messages[-1], dict) else getattr(messages[-1], "content", "")
    entities = extract_entities(latest_msg)

    activity: List[str] = state.get("activity", [])[:]
    sources: List[Dict[str, Any]] = state.get("sources", [])[:]
    pending_action = None
    status = "ANSWERED"

    try:
        order_details = []
        customer_details = []
        ticket_details = []
        target_customer = entities["customers"][0] if entities["customers"] else None

        for o_id in entities["orders"]:
            res = tool_get_order(order_id=o_id, user_context=user_context)
            if res.get("activity"):
                activity.append(res["activity"])
            if res.get("found"):
                order_details.append(res)
                if not target_customer and res.get("customer"):
                    target_customer = res["customer"]

        for t_id in entities["tickets"]:
            res = tool_get_ticket(ticket_id=t_id, user_context=user_context)
            if res.get("activity"):
                activity.append(res["activity"])
            if res.get("found"):
                ticket_details.append(res)
                if not target_customer and res.get("customer"):
                    target_customer = res["customer"]

        if target_customer:
            res = tool_get_customer(customer_name=target_customer, user_context=user_context)
            if res.get("activity"):
                activity.append(res["activity"])
            if res.get("found"):
                customer_details.append(res)

        msg_lower = latest_msg.lower()
        if "escalate" in msg_lower or "create escalation" in msg_lower:
            tkt_id = entities["tickets"][0] if entities["tickets"] else "TKT-501"
            esc_res = tool_create_escalation(
                ticket_id=tkt_id,
                reason=latest_msg,
                priority="high",
                user_context=user_context
            )
            if esc_res.get("activity"):
                activity.append(esc_res["activity"])
            pending_action = esc_res.get("pending_action")
            status = "ACTION_PENDING_CONFIRMATION"

        calc_res = None
        if "credit" in msg_lower or "sla" in msg_lower or "fee" in msg_lower:
            if entities["orders"]:
                calc_res = tool_calculate_service_credit(order_id=entities["orders"][0], user_context=user_context)
                if calc_res.get("activity"):
                    activity.append(calc_res["activity"])
                if calc_res.get("status") == "NEEDS_CLARIFICATION":
                    status = "NEEDS_CLARIFICATION"

        rag_res = tool_search_documents(
            query=latest_msg,
            customer_name=target_customer,
            top_k=5,
            user_context=user_context
        )
        if rag_res.get("activity"):
            activity.append(rag_res["activity"])

        for r in rag_res.get("results", []):
            if not any(s.get("text") == r["text"] for s in sources):
                sources.append(r)

        policy_eval = resolve_policy_precedence(sources, customer_name=target_customer)

        response_parts = []

        if order_details:
            od = order_details[0]
            response_parts.append(
                f"**Order Details ({od['order_id']})**:\n"
                f"- Customer: {od.get('customer', 'Unknown')}\n"
                f"- Carrier: {od.get('carrier', 'N/A')}\n"
                f"- Status: {od.get('status', 'N/A')}"
            )

        if ticket_details:
            td = ticket_details[0]
            response_parts.append(
                f"**Support Ticket ({td['ticket_id']})**:\n"
                f"- Customer: {td.get('customer', 'N/A')}\n"
                f"- Subject: {td.get('issue_type', 'N/A')}\n"
                f"- Status: {td.get('status', 'N/A')}"
            )

        if calc_res:
            if calc_res.get("status") == "NEEDS_CLARIFICATION":
                response_parts.append(f"**Service Credit Assessment**: {calc_res['reason']}")
            elif calc_res.get("eligible"):
                response_parts.append(
                    f"**Service Credit Eligible**: Verified carrier fault for order {calc_res['order_id']}. "
                    f"Eligible for {calc_res['credit_percentage']}% SLA credit (INR {calc_res['credit_amount_inr']:.2f})."
                )
            else:
                response_parts.append(f"**Service Credit Ineligible**: {calc_res['reason']}")

        if sources:
            response_parts.append("**Policy & Agreement Investigation Findings**:")
            for s in sources[:3]:
                doc_title = s.get("document", "Document")
                auth = s.get("authority", "general")
                page = s.get("page", 1)
                text = s.get("text", "").replace("\n", " ").strip()
                response_parts.append(f"• *{doc_title}* (Page {page}, {auth.upper()}): \"{text[:180]}...\"")

        if policy_eval["precedence_notes"]:
            response_parts.append("\n**Policy Hierarchy Notes**:\n" + "\n".join(f"- {note}" for note in policy_eval["precedence_notes"]))

        if pending_action:
            response_parts.append(f"\n⚠️ **Action Prepared**: {pending_action['summary']}. Requires human confirmation before execution.")

        final_response = "\n\n".join(response_parts) if response_parts else "No specific policy or operational records matched your query."

        return {
            "status": status,
            "final_response": final_response,
            "activity": list(dict.fromkeys(activity)),
            "sources": sources,
            "pending_action": pending_action
        }

    except SecurityError as sec_err:
        logger.warning(f"Security error handled in fallback node: {sec_err}")
        return {
            "status": "NEEDS_HUMAN_REVIEW",
            "final_response": f"🔒 **Security Authorization Error**: {str(sec_err)}",
            "activity": activity + ["⚠️ Blocked unauthorized account access attempt"],
            "sources": [],
            "pending_action": None
        }


def call_llm_node(state: AgentState) -> Dict[str, Any]:
    """
    Main LLM node invoking Google Gemini Chat Model with bound tools.
    Uses GEMINI_MODEL setting as single source of truth.
    """
    try:
        chat_model = get_chat_model()
    except LLMConfigError as cfg_err:
        logger.error("Gemini configuration error: %s", cfg_err)
        raise

    messages_input = state.get("messages", [])
    if not messages_input:
        return {"status": "NEEDS_CLARIFICATION", "final_response": "No prompt received."}

    lc_messages = [SystemMessage(content=SYSTEM_PROMPT)]
    for msg in messages_input[-10:]:
        if isinstance(msg, dict):
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "assistant":
                lc_messages.append(AIMessage(content=content))
            else:
                lc_messages.append(HumanMessage(content=content))
        elif hasattr(msg, "content"):
            lc_messages.append(msg)

    model_with_tools = chat_model.bind_tools(AGENT_TOOLS)

    try:
        response = model_with_tools.invoke(lc_messages)
        
        new_messages = list(messages_input) + [response]
        tool_calls = getattr(response, "tool_calls", [])
        if not tool_calls:
            return {
                "messages": new_messages,
                "status": "ANSWERED",
                "final_response": response.content
            }

        return {
            "messages": new_messages,
            "status": "IN_PROGRESS"
        }
    except Exception as e:
        logger.error("Gemini request failed: %s", e, exc_info=True)
        raise


def execute_tools_node(state: AgentState) -> Dict[str, Any]:
    """
    Tool execution node executing tool calls generated by the Chat LLM.
    Updates activity logs, sources, pending actions, and tool message history.
    """
    messages = state.get("messages", [])
    user_context = state.get("user_context", {})
    activity: List[str] = state.get("activity", [])[:]
    sources: List[Dict[str, Any]] = state.get("sources", [])[:]
    pending_action = state.get("pending_action")
    status = state.get("status", "ANSWERED")

    if not messages:
        return state

    last_message = messages[-1]
    tool_calls = getattr(last_message, "tool_calls", [])
    new_tool_messages = []

    for call in tool_calls:
        tool_name = call.get("name")
        args = call.get("args", {})
        call_id = call.get("id")

        fn = TOOL_MAP.get(tool_name)
        if not fn:
            result_str = f"Error: Tool '{tool_name}' not found."
        else:
            try:
                # Add user_context to kwargs if function accepts it
                kwargs = dict(args)
                result = fn(**kwargs, user_context=user_context) if "user_context" not in kwargs else fn(**kwargs)

                if isinstance(result, dict):
                    if result.get("activity"):
                        activity.append(result["activity"])
                    if tool_name == "search_documents":
                        for r in result.get("results", []):
                            if not any(s.get("text") == r["text"] for s in sources):
                                sources.append(r)
                    if tool_name == "create_escalation":
                        pending_action = result.get("pending_action")
                        status = "ACTION_PENDING_CONFIRMATION"

                result_str = json.dumps(sanitize_json_obj(result), default=str)
            except SecurityError as sec_err:
                logger.warning(f"Security error in tool '{tool_name}': {sec_err}")
                activity.append("⚠️ Blocked unauthorized account access attempt")
                status = "NEEDS_HUMAN_REVIEW"
                result_str = f"🔒 Security Error: {str(sec_err)}"
            except Exception as ex:
                logger.error(f"Error executing tool '{tool_name}': {ex}", exc_info=True)
                result_str = f"Error executing tool '{tool_name}': {str(ex)}"

        new_tool_messages.append(ToolMessage(content=result_str, tool_call_id=call_id))

    return {
        "messages": messages + new_tool_messages,
        "activity": list(dict.fromkeys(activity)),
        "sources": sources,
        "pending_action": pending_action,
        "status": status
    }
