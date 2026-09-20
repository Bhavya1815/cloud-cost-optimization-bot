from .approval_store import (
    get_approval_request,
    update_approval_status,
)
from .scanner import scan_ec2_instances
from .idle_detector import analyze_idle_instances
from .remediation import stop_instance


def execute_approved_remediation(
    approval_id
):
    """
    Execute remediation only when an approval
    request has been explicitly approved.
    """

    approval = get_approval_request(
        approval_id
    )

    if not approval:
        return {
            "success": False,
            "reason": "Approval request not found.",
        }

    if approval.get("status") != "APPROVED":
        return {
            "success": False,
            "reason": (
                "Approval request is not approved. "
                f"Current status: {approval.get('status')}"
            ),
        }

    instances = scan_ec2_instances()

    instances = analyze_idle_instances(
        instances
    )

    target_instances = [
        instance
        for instance in instances
        if instance["instance_id"]
        == approval["instance_id"]
    ]

    if not target_instances:
        update_approval_status(
            approval_id,
            "FAILED",
        )

        return {
            "success": False,
            "reason": (
                "Target instance is no longer "
                "running or available."
            ),
        }

    instance = target_instances[0]

    result = stop_instance(
        instance
    )

    if result["success"]:

        update_approval_status(
            approval_id,
            "EXECUTED",
        )

        return {
            "success": True,
            "instance_id": instance["instance_id"],
            "reason": (
                "Approved remediation executed "
                "successfully."
            ),
        }

    update_approval_status(
        approval_id,
        "FAILED",
    )

    return {
        "success": False,
        "instance_id": instance["instance_id"],
        "reason": result["reason"],
    }