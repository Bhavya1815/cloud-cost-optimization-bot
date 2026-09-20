from app.approval import (
    create_approval_request,
    approve_request,
    reject_request,
)


def sample_recommendation():
    return {
        "instance_id": "i-test-1",
        "name": "dev-idle-01",
        "action": "STOP",
    }


def test_approval_request_starts_pending():
    approval = create_approval_request(
        sample_recommendation()
    )

    assert approval["status"] == "PENDING"
    assert approval["instance_id"] == "i-test-1"
    assert approval["action"] == "STOP"
    assert approval["approval_id"]


def test_pending_request_can_be_approved():
    approval = create_approval_request(
        sample_recommendation()
    )

    result = approve_request(approval)

    assert result["success"] is True
    assert result["approval"]["status"] == "APPROVED"
    assert "approved_at" in result["approval"]


def test_pending_request_can_be_rejected():
    approval = create_approval_request(
        sample_recommendation()
    )

    result = reject_request(approval)

    assert result["success"] is True
    assert result["approval"]["status"] == "REJECTED"
    assert "rejected_at" in result["approval"]


def test_approved_request_cannot_be_reapproved():
    approval = create_approval_request(
        sample_recommendation()
    )

    approve_request(approval)
    result = approve_request(approval)

    assert result["success"] is False


def test_rejected_request_cannot_be_reapproved():
    approval = create_approval_request(
        sample_recommendation()
    )

    reject_request(approval)
    result = approve_request(approval)

    assert result["success"] is False