from app.remediation import can_stop_instance


def base_instance():
    return {
        "instance_id": "i-test-1",
        "state": "running",
        "environment": "dev",
        "critical": "false",
        "cost_optimization": "true",
        "idle": True,
    }


def test_eligible_instance_can_be_stopped():
    allowed, reason = can_stop_instance(
        base_instance()
    )

    assert allowed is True
    assert reason == "Instance passed all safety checks."


def test_production_instance_cannot_be_stopped():
    instance = base_instance()
    instance["environment"] = "prod"

    allowed, reason = can_stop_instance(instance)

    assert allowed is False
    assert reason == "Production instances cannot be stopped."


def test_critical_instance_cannot_be_stopped():
    instance = base_instance()
    instance["critical"] = "true"

    allowed, reason = can_stop_instance(instance)

    assert allowed is False
    assert reason == "Critical instances cannot be stopped."


def test_non_optimized_instance_cannot_be_stopped():
    instance = base_instance()
    instance["cost_optimization"] = "false"

    allowed, reason = can_stop_instance(instance)

    assert allowed is False
    assert (
        reason
        == "Instance is not marked for cost optimization."
    )


def test_active_instance_cannot_be_stopped():
    instance = base_instance()
    instance["idle"] = False

    allowed, reason = can_stop_instance(instance)

    assert allowed is False
    assert reason == "Instance is not currently idle."


def test_stopped_instance_cannot_be_stopped():
    instance = base_instance()
    instance["state"] = "stopped"

    allowed, reason = can_stop_instance(instance)

    assert allowed is False
    assert reason == "Instance is not running."