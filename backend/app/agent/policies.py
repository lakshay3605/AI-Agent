"""Policy Precedence and Document Conflict Resolution Helper."""

import logging
from typing import List, Dict, Any

logger = logging.getLogger("parcelpilot.policies")


def resolve_policy_precedence(sources: List[Dict[str, Any]], customer_name: str = None) -> Dict[str, Any]:
    """
    Evaluate retrieved RAG sources according to ParcelPilot policy hierarchy:
    1. Customer Enterprise Agreement (highest priority for customer-specific queries)
    2. Current SOP (03_Cancellation_and_Service_Credit_SOP_v4.pdf)
    3. Current Policy (01_Support_Policy_v3_CURRENT.pdf)
    4. Product / Ops Guide (04_Product_Operations_Guide_and_Known_Issues.pdf)
    5. Deprecated Policy (02_Support_Policy_v2_DEPRECATED.pdf) -> Flagged as superseded
    """
    has_deprecated = False
    deprecated_docs = []
    has_customer_agreement = False
    customer_agreement_doc = None
    sop_doc = None
    current_policy_doc = None

    for src in sources:
        status = src.get("status", "current")
        auth = src.get("authority", "general")
        doc_name = src.get("document", "")

        if status == "deprecated":
            has_deprecated = True
            deprecated_docs.append(doc_name)
        elif auth == "customer_agreement":
            has_customer_agreement = True
            customer_agreement_doc = doc_name
        elif auth == "sop":
            sop_doc = doc_name
        elif auth == "general_policy":
            current_policy_doc = doc_name

    precedence_notes = []
    if has_customer_agreement:
        precedence_notes.append(f"Customer agreement '{customer_agreement_doc}' takes precedence for account terms.")
    if sop_doc:
        precedence_notes.append(f"Standard operating procedure '{sop_doc}' governs processing steps.")
    if has_deprecated:
        precedence_notes.append(f"Note: Retrieved reference '{', '.join(deprecated_docs)}' is DEPRECATED and superseded by current policy.")

    return {
        "has_customer_agreement": has_customer_agreement,
        "has_deprecated": has_deprecated,
        "precedence_notes": precedence_notes
    }
