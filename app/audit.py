from datetime import datetime, timezone
import uuid


AUDIT_EVENT_TYPES = {
    "SCAN_STARTED",
    "SCAN_COMPLETED",
    "SCAN_FAILED",
    "RECOMMENDATION_DETECTED",
    "APPROVAL_CREATED",
    "APPROVAL_APPROVED",
    "APPROVAL_REJECTED",
    "ALERT_SENT",
    "UNAUTHORIZED_COMMAND",
    "REMEDIATION_REQUESTED",
    "REMEDIATION_BLOCKED",
    "REMEDIATION_EXECUTED",
    "REMEDIATION_FAILED",
}


def build_audit_event(
    event_type,
    *,
    instance_id=None,
    name=None,
    approval_id=None,
    status=None,
    message=None,
    metadata=None,
):
    if event_type not in AUDIT_EVENT_TYPES:
        raise ValueError(
            f"Unsupported audit event type: {event_type}"
        )

    event = {
        "event_id": str(uuid.uuid4()),
        "event_type": event_type,
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
    }

    optional_fields = {
        "instance_id": instance_id,
        "name": name,
        "approval_id": approval_id,
        "status": status,
        "message": message,
        "metadata": metadata,
    }

    for key, value in optional_fields.items():
        if value is not None:
            event[key] = value

    return event