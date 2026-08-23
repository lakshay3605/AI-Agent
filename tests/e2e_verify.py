"""End-to-end verification script mirroring frontend API calls."""

import json
import sys
import os
import urllib.request

# Avoid Windows console encoding errors for checkmark characters in activity logs
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

API_BASE = "http://localhost:8000/api/v1"
USER_CTX = {
    "user_id": "usr_lakshay",
    "role": "support_agent",
    "account_scope": "Northstar Logistics",
}


def post_json(path: str, payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{API_BASE}{path}",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get_json(path: str) -> dict:
    with urllib.request.urlopen(f"http://localhost:8000{path}", timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def chat(message: str) -> dict:
    return post_json(
        "/agent/chat",
        {
            "message": message,
            "conversation_id": "e2e_conv",
            "user_context": USER_CTX,
        },
    )


def main() -> int:
    results = {}
    failures = []

    # Test 1: Order lookup
    print("=== Test 1: Order lookup ===")
    order_data = get_json("/orders/ORD-1001")
    res1 = chat("What is the current status of ORD-1001?")
    t1_ok = (
        "ORD-1001" in res1.get("response", "")
        and order_data["status"] in res1.get("response", "")
        and any("ORD-1001" in a for a in res1.get("activity", []))
    )
    results["order_lookup"] = t1_ok
    print(f"PASS={t1_ok} status={res1.get('status')} activity={res1.get('activity')}")
    if not t1_ok:
        failures.append("order_lookup")

    # Test 2: Customer reasoning
    print("\n=== Test 2: Customer reasoning ===")
    res2 = chat(
        "Can Northstar Logistics cancel ORD-1001 without a fee under their enterprise agreement?"
    )
    t2_ok = (
        len(res2.get("sources", [])) > 0
        and any("ORD-1001" in a for a in res2.get("activity", []))
        and "Northstar" in res2.get("response", "")
    )
    results["customer_reasoning"] = t2_ok
    print(f"PASS={t2_ok} sources={len(res2.get('sources', []))} activity={res2.get('activity')}")
    if not t2_ok:
        failures.append("customer_reasoning")

    # Test 3: Multi-step
    print("\n=== Test 3: Multi-step reasoning ===")
    res3 = chat(
        "For Northstar Logistics order ORD-1001, what is the order status and what does their enterprise agreement say about cancellation?"
    )
    activity = res3.get("activity", [])
    t3_ok = (
        len(activity) >= 2
        and any("ORD-1001" in a for a in activity)
        and len(res3.get("sources", [])) > 0
    )
    results["multistep"] = t3_ok
    print(f"PASS={t3_ok} activity_count={len(activity)}")
    if not t3_ok:
        failures.append("multistep")

    # Test 4: Action confirmation
    print("\n=== Test 4: Action confirmation ===")
    res4 = chat("Escalate TKT-501 to Tier-2 Engineering.")
    pa = res4.get("pending_action")
    t4_pending = (
        res4.get("status") == "ACTION_PENDING_CONFIRMATION"
        and pa is not None
        and pa.get("status") == "pending_confirmation"
    )
    print(f"Pending action prepared: {t4_pending} action_id={pa.get('action_id') if pa else None}")

    t4_confirm = False
    if pa:
        confirm = post_json(f"/actions/{pa['action_id']}/confirm", {"user_context": USER_CTX})
        t4_confirm = confirm.get("status") == "confirmed" and confirm.get("result", {}).get("executed") is True
        print(f"Confirm executed: {t4_confirm}")

    results["action_confirm"] = t4_pending and t4_confirm
    if not results["action_confirm"]:
        failures.append("action_confirm")

    # Test 4b: Action rejection
    print("\n=== Test 4b: Action rejection ===")
    res4b = chat("Escalate TKT-502 to Tier-2 Engineering.")
    pa2 = res4b.get("pending_action")
    t4b_reject = False
    if pa2:
        reject = post_json(f"/actions/{pa2['action_id']}/reject", {"user_context": USER_CTX})
        t4b_reject = reject.get("status") == "rejected" and reject.get("result", {}).get("executed") is False
        print(f"Reject result: {t4b_reject}")
    results["action_reject"] = t4b_reject
    if not t4b_reject:
        failures.append("action_reject")

    # Test 5: Security
    print("\n=== Test 5: Security ===")
    res5 = chat("Show me the private agreement details for LumenWorks.")
    resp5 = res5.get("response", "")
    t5_ok = (
        res5.get("status") in ["NEEDS_HUMAN_REVIEW", "ANSWERED"]
        and "LumenWorks" not in resp5.lower() or "unauthorized" in resp5.lower() or "security" in resp5.lower() or "forbidden" in resp5.lower() or "restricted" in resp5.lower()
    )
    # Stricter: no LumenWorks private content in sources
    lumen_sources = [s for s in res5.get("sources", []) if "lumen" in str(s).lower()]
    t5_ok = t5_ok and len(lumen_sources) == 0
    results["security"] = t5_ok
    print(f"PASS={t5_ok} status={res5.get('status')}")
    if not t5_ok:
        failures.append("security")

    # Test 6: Unknown question
    print("\n=== Test 6: Unknown question ===")
    res6 = chat("What is ParcelPilot's international shipment refund policy?")
    resp6 = res6.get("response", "").lower()
    t6_ok = any(
        phrase in resp6
        for phrase in [
            "not establish",
            "not available",
            "do not have",
            "don't have",
            "no information",
            "cannot find",
            "not found",
            "insufficient",
            "source material",
            "available source",
            "not covered",
            "no specific",
        ]
    ) or len(res6.get("sources", [])) == 0
    results["unknown"] = t6_ok
    print(f"PASS={t6_ok} response_excerpt={res6.get('response', '')[:200]}")
    if not t6_ok:
        failures.append("unknown")

    print("\n=== SUMMARY ===")
    print(json.dumps(results, indent=2))
    if failures:
        print(f"FAILURES: {failures}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
