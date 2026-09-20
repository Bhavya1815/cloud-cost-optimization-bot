import uuid
from datetime import datetime, timezone


APPROVAL_EXPIRY_HOURS = 24


def create_approval_request(recommendation):
    """
    Create an approval request for a remediation action.
    """

    now = datetime.now(timezone.utc)

    return {
        "approval_id": str(uuid.uuid4()),
        "instance_id": recommendation["instance_id"],
        "name": recommendation["name"],
        "action": recommendation["action"],
        "status": "PENDING",
        "created_at": now.isoformat(),
        "expires_in_hours": APPROVAL_EXPIRY_HOURS,
    }


def approve_request(approval):
    """
    Approve a pending remediation request.
    """

    if approval["status"] != "PENDING":
        return {
            "success": False,
            "reason": (
                f"Request is already "
                f"{approval['status']}."
            ),
        }

    approval["status"] = "APPROVED"
    approval["approved_at"] = (
        datetime.now(timezone.utc).isoformat()
    )

    return {
        "success": True,
        "approval": approval,
    }


def reject_request(approval):
    """
    Reject a pending remediation request.
    """

    if approval["status"] != "PENDING":
        return {
            "success": False,
            "reason": (
                f"Request is already "
                f"{approval['status']}."
            ),
        }

    approval["status"] = "REJECTED"
    approval["rejected_at"] = (
        datetime.now(timezone.utc).isoformat()
    )

    return {
        "success": True,
        "approval": approval,
    }