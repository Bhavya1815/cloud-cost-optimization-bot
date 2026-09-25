from .providers.pricing import get_pricing_provider


def estimate_monthly_cost(
    instance_type,
    instance_id=None,
):
    provider = get_pricing_provider()

    return provider.estimate_monthly_cost(
        instance_type,
        instance_id,
    )


def add_cost_estimates(recommendations):
    for recommendation in recommendations:
        monthly_cost = estimate_monthly_cost(
            recommendation["instance_type"],
            recommendation["instance_id"],
        )

        recommendation[
            "estimated_monthly_cost"
        ] = monthly_cost

        recommendation[
            "estimated_monthly_savings"
        ] = monthly_cost

        recommendation[
            "cost_source"
        ] = get_pricing_provider().source_name

    return recommendations
