from .approval_store import (
    get_approval_request,
    update_approval_status,
)
from .scanner import scan_ec2_instances
from .idle_detector import (
    analyze_idle_instances,
)
from .remediation import stop_instance
from .logging_config import (
    get_logger,
)
from .audit_store import (
    safe_record_audit_event,
)


logger = get_logger(__name__)


def execute_approved_remediation(
    approval_id,
):
    safe_record_audit_event(
        logger,
        "REMEDIATION_REQUESTED",
        approval_id=approval_id,
        status="REQUESTED",
    )

    approval = get_approval_request(
        approval_id
    )

    if not approval:
        safe_record_audit_event(
            logger,
            "REMEDIATION_FAILED",
            approval_id=approval_id,
            status="FAILED",
            message="Approval request not found.",
        )

        return {
            "success": False,
            "reason": (
                "Approval request not found."
            ),
        }

    if approval.get("status") != "APPROVED":
        reason = (
            "Approval request is not approved. "
            f"Current status: "
            f"{approval.get('status')}"
        )

        safe_record_audit_event(
            logger,
            "REMEDIATION_BLOCKED",
            instance_id=approval.get(
                "instance_id"
            ),
            name=approval.get("name"),
            approval_id=approval_id,
            status=approval.get("status"),
            message=reason,
        )

        return {
            "success": False,
            "reason": reason,
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

        reason = (
            "Target instance is no longer "
            "running or available."
        )

        safe_record_audit_event(
            logger,
            "REMEDIATION_FAILED",
            instance_id=approval.get(
                "instance_id"
            ),
            name=approval.get("name"),
            approval_id=approval_id,
            status="FAILED",
            message=reason,
        )

        return {
            "success": False,
            "reason": reason,
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

        safe_record_audit_event(
            logger,
            "REMEDIATION_EXECUTED",
            instance_id=instance[
                "instance_id"
            ],
            name=instance.get("name"),
            approval_id=approval_id,
            status="EXECUTED",
            message=result["reason"],
        )

        return {
            "success": True,
            "instance_id": instance[
                "instance_id"
            ],
            "reason": (
                "Approved remediation "
                "executed successfully."
            ),
        }

    update_approval_status(
        approval_id,
        "FAILED",
    )

    safe_record_audit_event(
        logger,
        "REMEDIATION_FAILED",
        instance_id=instance[
            "instance_id"
        ],
        name=instance.get("name"),
        approval_id=approval_id,
        status="FAILED",
        message=result["reason"],
    )

    return {
        "success": False,
        "instance_id": instance[
            "instance_id"
        ],
        "reason": result["reason"],
    }
