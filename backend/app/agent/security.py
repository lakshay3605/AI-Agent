"""Security and Authorization Context Scoping for ParcelPilot AI Agent."""

import logging
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

logger = logging.getLogger("parcelpilot.security")


class UserContext(BaseModel):
    """User Context passed into agent execution and tool layers."""
    user_id: str = Field(default="usr_default", description="User ID of human executive")
    role: str = Field(default="support_agent", description="Role: support_agent, operations_executive, admin")
    account_scope: Optional[str] = Field(default=None, description="Optional customer scope constraint (e.g. Northstar Logistics)")


class SecurityError(Exception):
    """Custom exception raised when a security/scope violation occurs."""
    pass


def validate_access(user_context: Optional[Dict[str, Any]], target_customer: Optional[str]) -> None:
    """
    Verify that the user context has permission to access target customer data.
    Raises SecurityError if user is scoped to a different customer account.
    """
    if not user_context:
        return

    # Extract account_scope if present
    scope = user_context.get("account_scope")
    if scope and target_customer:
        scope_norm = scope.strip().lower()
        target_norm = target_customer.strip().lower()
        if scope_norm != target_norm and scope_norm not in target_norm and target_norm not in scope_norm:
            logger.warning(f"Unauthorized access attempt by user scoped to '{scope}' accessing '{target_customer}'")
            raise SecurityError(
                f"Unauthorized access: User scope is restricted to '{scope}'. Access to '{target_customer}' data is forbidden."
            )
