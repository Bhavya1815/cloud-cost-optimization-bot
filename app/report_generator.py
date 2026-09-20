from datetime import datetime, timezone


def generate_weekly_report(recommendations):
    """
    Generate a weekly cost optimization report.

    Cost figures are simulated estimates for the
    local Floci environment.
    """

    timestamp = datetime.now(timezone.utc).strftime(
        "%Y-%m-%d %H:%M:%S UTC"
    )

    total_savings = sum(
        recommendation["estimated_monthly_savings"]
        for recommendation in recommendations
    )

    lines = [
        "CLOUD COST OPTIMIZATION - WEEKLY REPORT",
        "=" * 50,
        "",
        f"Generated: {timestamp}",
        "",
        f"Optimization Candidates: {len(recommendations)}",
        f"Estimated Monthly Savings: ${total_savings:.2f}",
        "",
    ]

    if not recommendations:
        lines.append(
            "No optimization candidates detected."
        )

        return "\n".join(lines)

    lines.extend([
        "RESOURCE DETAILS",
        "-" * 50,
    ])

    for recommendation in recommendations:
        lines.extend([
            f"Name: {recommendation['name']}",
            f"Instance ID: {recommendation['instance_id']}",
            f"Instance Type: {recommendation['instance_type']}",
            f"CPU Utilization: {recommendation['cpu_utilization']}%",
            f"Action: {recommendation['action']}",
            (
                "Estimated Monthly Saving: "
                f"${recommendation['estimated_monthly_savings']:.2f}"
            ),
            "",
        ])

    lines.extend([
        "=" * 50,
        f"TOTAL ESTIMATED SAVINGS: ${total_savings:.2f}/month",
        "",
        "Note: Cost figures are simulated estimates "
        "for the Floci local environment.",
    ])

    return "\n".join(lines)
