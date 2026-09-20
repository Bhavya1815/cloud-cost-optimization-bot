from app.cost_engine import (
    estimate_monthly_cost,
    add_cost_estimates,
)


def test_t2_micro_monthly_cost():
    assert estimate_monthly_cost("t2.micro") == 8.47


def test_unknown_instance_type_has_zero_cost():
    assert estimate_monthly_cost("unknown.type") == 0


def test_cost_estimates_are_added():
    recommendations = [
        {
            "instance_id": "i-test-1",
            "name": "dev-idle-01",
            "instance_type": "t2.micro",
            "action": "STOP",
        }
    ]

    result = add_cost_estimates(recommendations)

    assert result[0]["estimated_monthly_cost"] == 8.47
    assert result[0]["estimated_monthly_savings"] == 8.47