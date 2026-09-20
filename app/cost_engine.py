from .config import (
    SIMULATED_HOURLY_RATES,
    HOURS_PER_MONTH,
)


def estimate_monthly_cost(instance_type):
    """
    Estimate monthly EC2 cost using simulated rates.

    These values are for local Floci testing only
    and do not represent actual AWS billing.
    """

    hourly_rate = SIMULATED_HOURLY_RATES.get(
        instance_type,
        0
    )

    return round(
        hourly_rate * HOURS_PER_MONTH,
        2
    )


def add_cost_estimates(recommendations):
    """
    Add estimated monthly cost and savings
    to each recommendation.
    """

    for recommendation in recommendations:

        monthly_cost = estimate_monthly_cost(
            recommendation["instance_type"]
        )

        recommendation["estimated_monthly_cost"] = monthly_cost

        recommendation["estimated_monthly_savings"] = monthly_cost

    return recommendations
