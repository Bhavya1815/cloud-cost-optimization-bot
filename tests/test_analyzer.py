from app.analyzer import analyze_instances


def test_idle_non_production_resource_is_candidate():
    instances = [
        {
            "instance_id": "i-test-1",
            "name": "dev-idle-01",
            "instance_type": "t2.micro",
            "state": "running",
            "environment": "dev",
            "cost_optimization": "true",
            "critical": "false",
            "idle": True,
            "cpu_utilization": 4.25,
        }
    ]

    recommendations = analyze_instances(instances)

    assert len(recommendations) == 1
    assert recommendations[0]["action"] == "STOP"
    assert recommendations[0]["instance_id"] == "i-test-1"


def test_production_resource_is_not_candidate():
    instances = [
        {
            "instance_id": "i-prod-1",
            "name": "production-01",
            "instance_type": "t3.small",
            "state": "running",
            "environment": "prod",
            "cost_optimization": "true",
            "critical": "false",
            "idle": True,
            "cpu_utilization": 3.0,
        }
    ]

    assert analyze_instances(instances) == []


def test_critical_resource_is_not_candidate():
    instances = [
        {
            "instance_id": "i-critical-1",
            "name": "dev-critical-01",
            "instance_type": "t2.micro",
            "state": "running",
            "environment": "dev",
            "cost_optimization": "true",
            "critical": "true",
            "idle": True,
            "cpu_utilization": 2.5,
        }
    ]

    assert analyze_instances(instances) == []


def test_non_optimized_resource_is_not_candidate():
    instances = [
        {
            "instance_id": "i-no-opt-1",
            "name": "dev-no-opt-01",
            "instance_type": "t2.micro",
            "state": "running",
            "environment": "dev",
            "cost_optimization": "false",
            "critical": "false",
            "idle": True,
            "cpu_utilization": 1.5,
        }
    ]

    assert analyze_instances(instances) == []


def test_active_resource_is_not_candidate():
    instances = [
        {
            "instance_id": "i-active-1",
            "name": "dev-active-01",
            "instance_type": "t3.micro",
            "state": "running",
            "environment": "dev",
            "cost_optimization": "true",
            "critical": "false",
            "idle": False,
            "cpu_utilization": 65.0,
        }
    ]

    assert analyze_instances(instances) == []