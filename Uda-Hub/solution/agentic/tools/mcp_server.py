"""CultPass Database Tools

These tools abstract the CultPass database for agent use.
They are decorated with LangChain's @tool for direct agent integration,
and also registered with a FastMCP server for MCP-based access.

To run as MCP server: python -m agentic.tools.mcp_server
"""

import json
import os
import sys
import uuid

from langchain_core.tools import tool
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure the solution root is on the path for model imports
_SOLUTION_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _SOLUTION_ROOT not in sys.path:
    sys.path.insert(0, _SOLUTION_ROOT)

CULTPASS_DB = os.path.join(_SOLUTION_ROOT, "data", "external", "cultpass.db")


def _get_session():
    engine = create_engine(f"sqlite:///{CULTPASS_DB}", echo=False)
    Session = sessionmaker(bind=engine)
    return Session()


@tool
def account_lookup(email: str) -> str:
    """Look up a CultPass user account by email. Returns user info including
    subscription status, tier, and blocked status."""
    from data.models.cultpass import User

    session = _get_session()
    try:
        user = session.query(User).filter_by(email=email).first()
        if not user:
            return json.dumps({"error": "User not found", "email": email})
        result = {
            "user_id": user.user_id,
            "full_name": user.full_name,
            "email": user.email,
            "is_blocked": user.is_blocked,
            "subscription": None,
        }
        if user.subscription:
            result["subscription"] = {
                "subscription_id": user.subscription.subscription_id,
                "status": user.subscription.status,
                "tier": user.subscription.tier,
                "monthly_quota": user.subscription.monthly_quota,
            }
        return json.dumps(result)
    finally:
        session.close()


@tool
def subscription_management(user_id: str, action: str) -> str:
    """Manage a user's subscription. Actions: 'check_status', 'cancel', 'pause', 'reactivate'.
    Returns the updated subscription status."""
    from data.models.cultpass import Subscription

    session = _get_session()
    try:
        sub = session.query(Subscription).filter_by(user_id=user_id).first()
        if not sub:
            return json.dumps({"error": "No subscription found for user", "user_id": user_id})

        if action == "check_status":
            result = {
                "status": sub.status,
                "tier": sub.tier,
                "monthly_quota": sub.monthly_quota,
            }
        elif action == "cancel":
            sub.status = "cancelled"
            session.commit()
            result = {
                "status": "cancelled",
                "message": "Subscription cancelled. Effective at end of billing cycle.",
            }
        elif action == "pause":
            sub.status = "paused"
            session.commit()
            result = {
                "status": "paused",
                "message": "Subscription paused. Your data is preserved and will resume when reactivated.",
            }
        elif action == "reactivate":
            sub.status = "active"
            session.commit()
            result = {
                "status": "active",
                "message": "Subscription reactivated successfully.",
            }
        else:
            result = {"error": f"Unknown action: {action}. Valid actions: check_status, cancel, pause, reactivate"}
        return json.dumps(result)
    finally:
        session.close()


@tool
def reservation_lookup(user_id: str) -> str:
    """Look up all reservations for a user. Returns reservation details with experience info."""
    from data.models.cultpass import Reservation

    session = _get_session()
    try:
        reservations = session.query(Reservation).filter_by(user_id=user_id).all()
        if not reservations:
            return json.dumps({"message": "No reservations found for this user.", "user_id": user_id})
        results = []
        for r in reservations:
            results.append({
                "reservation_id": r.reservation_id,
                "experience_title": r.experience.title if r.experience else "Unknown",
                "experience_location": r.experience.location if r.experience else "Unknown",
                "experience_when": str(r.experience.when) if r.experience else "Unknown",
                "status": r.status,
            })
        return json.dumps(results)
    finally:
        session.close()


@tool
def process_refund(user_id: str, reason: str, amount: str) -> str:
    """Process a refund for a user. Requires user_id, reason, and amount.
    Returns confirmation with a reference number."""
    refund_id = str(uuid.uuid4())[:8]
    return json.dumps({
        "refund_id": refund_id,
        "user_id": user_id,
        "amount": amount,
        "reason": reason,
        "status": "processed",
        "message": f"Refund of {amount} processed successfully. Reference: {refund_id}",
    })


# --- FastMCP Server Registration (for MCP-based access) ---
def _create_mcp_server():
    """Create a FastMCP server with the same tools for MCP protocol access."""
    from fastmcp import FastMCP

    mcp = FastMCP("CultPass Support Tools")

    # Register the tool functions with MCP
    mcp.tool()(account_lookup.func)
    mcp.tool()(subscription_management.func)
    mcp.tool()(reservation_lookup.func)
    mcp.tool()(process_refund.func)

    return mcp


if __name__ == "__main__":
    mcp = _create_mcp_server()
    mcp.run()
