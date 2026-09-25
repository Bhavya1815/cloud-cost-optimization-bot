from app.remediation import can_stop_instance


def base_instance():
    return {
        "instance_id": "i-security-test",
        "state": "running",
        "environment": "dev",
        "critical": "false",
        "cost_optimization": "true",
        "idle": True,
    }


def test_running_idle_dev_resource_is_allowed():
    allowed, _ = can_stop_instance(
        base_instance()
    )

    assert allowed is True


def test_production_resource_is_blocked():
    instance = base_instance()
    instance["environment"] = "prod"

    allowed, reason = can_stop_instance(
        instance
    )

    assert allowed is False
    assert "Production" in reason


def test_critical_resource_is_blocked():
    instance = base_instance()
    instance["critical"] = "true"

    allowed, reason = can_stop_instance(
        instance
    )

    assert allowed is False
    assert "Critical" in reason


def test_active_resource_is_blocked():
    instance = base_instance()
    instance["idle"] = False

    allowed, reason = can_stop_instance(
        instance
    )

    assert allowed is False
    assert "idle" in reason


def test_stopped_resource_is_blocked():
    instance = base_instance()
    instance["state"] = "stopped"

    allowed, reason = can_stop_instance(
        instance
    )

    assert allowed is False
    assert "not running" in reason