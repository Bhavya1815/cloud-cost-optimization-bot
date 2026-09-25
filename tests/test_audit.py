from app.audit import (
    AUDIT_EVENT_TYPES,
    build_audit_event,
)


def test_build_audit_event_contains_required_fields():
    event = build_audit_event(
        "SCAN_STARTED"
    )

    assert event["event_id"]
    assert event["event_type"] == "SCAN_STARTED"
    assert event["timestamp"]


def test_build_audit_event_supports_optional_fields():
    event = build_audit_event(
        "APPROVAL_CREATED",
        instance_id="i-test",
        name="dev-test",
        approval_id="approval-test",
        status="PENDING",
        message="Approval created.",
        metadata={
            "source": "scheduler"
        },
    )

    assert event["instance_id"] == "i-test"
    assert event["name"] == "dev-test"
    assert event["approval_id"] == "approval-test"
    assert event["status"] == "PENDING"
    assert event["metadata"]["source"] == "scheduler"


def test_invalid_audit_event_type_is_rejected():
    try:
        build_audit_event(
            "INVALID_EVENT"
        )
    except ValueError:
        return

    assert False


def test_all_expected_event_types_are_defined():
    expected = {
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

    assert expected.issubset(
        AUDIT_EVENT_TYPES
    )


def test_audit_event_supports_remediation():
    event = build_audit_event(
        "REMEDIATION_EXECUTED",
        instance_id="i-test",
        approval_id="approval-test",
        status="EXECUTED",
        message="Instance stopped.",
    )

    assert event["event_type"] == (
        "REMEDIATION_EXECUTED"
    )

    assert event["status"] == "EXECUTED"


def test_audit_event_supports_unauthorized_command():
    event = build_audit_event(
        "UNAUTHORIZED_COMMAND",
        status="BLOCKED",
        message="/approve",
    )

    assert event["event_type"] == (
        "UNAUTHORIZED_COMMAND"
    )

    assert event["status"] == "BLOCKED"
