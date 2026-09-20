def format_recommendation_alert(recommendations):
    if not recommendations:
        return (
            "CLOUD COST OPTIMIZATION BOT\n\n"
            "No optimization candidates detected."
        )

    lines = [
        "CLOUD COST OPTIMIZATION ALERT",
        "",
        f"{len(recommendations)} optimization candidate(s) detected.",
        "",
    ]

    total_savings = 0

    for recommendation in recommendations:
        savings = recommendation["estimated_monthly_savings"]
        total_savings += savings

        lines.extend([
            f"Resource: {recommendation['name']}",
            f"Type: {recommendation['instance_type']}",
            f"Action: {recommendation['action']}",
            f"Estimated saving: ${savings:.2f}/month",
            f"Reason: {recommendation['reason']}",
            "",
        ])

    lines.append(
        f"TOTAL ESTIMATED SAVINGS: ${total_savings:.2f}/month"
    )

    return "\n".join(lines)
