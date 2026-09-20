from .scanner import scan_ec2_instances
from .idle_detector import analyze_idle_instances
from .analyzer import analyze_instances
from .cost_engine import add_cost_estimates
from .dynamodb_store import save_recommendations
from .telegram_formatter import format_recommendation_alert
from .telegram_notifier import send_message


def main():
    print("=" * 60)
    print("CLOUD COST OPTIMIZATION BOT")
    print("=" * 60)

    # Step 1: Discover EC2 instances
    instances = scan_ec2_instances()

    print(f"\nDiscovered {len(instances)} EC2 instance(s).\n")

    for instance in instances:
        print(
            f"Name:              {instance['name']}\n"
            f"Instance ID:       {instance['instance_id']}\n"
            f"Instance Type:     {instance['instance_type']}\n"
            f"State:             {instance['state']}\n"
            f"Environment:       {instance['environment']}\n"
            f"Cost Optimization: {instance['cost_optimization']}\n"
            f"Critical:           {instance['critical']}\n"
            f"{'-' * 60}"
        )

    # Step 2: Detect idle instances
    instances = analyze_idle_instances(instances)

    print("\nRESOURCE UTILIZATION")
    print("=" * 60)

    for instance in instances:
        print(
            f"Name:              {instance['name']}\n"
            f"CPU Utilization:   {instance['cpu_utilization']}%\n"
            f"Idle:              {instance['idle']}\n"
            f"Metric Source:     {instance['metric_source']}\n"
            f"{'-' * 60}"
        )

    # Step 3: Analyze instances
    recommendations = analyze_instances(instances)

    # Step 4: Calculate estimated costs and savings
    recommendations = add_cost_estimates(recommendations)

    print("\nCOST OPTIMIZATION RECOMMENDATIONS")
    print("=" * 60)

    if not recommendations:
        print("No optimization candidates found.")

        telegram_message = format_recommendation_alert(
            recommendations
        )

        send_message(telegram_message)

        print("Telegram alert sent successfully.")
        return

    # Step 5: Display recommendations
    total_savings = 0

    for recommendation in recommendations:
        total_savings += recommendation[
            "estimated_monthly_savings"
        ]

        print(
            f"Name:                     {recommendation['name']}\n"
            f"Instance ID:              {recommendation['instance_id']}\n"
            f"Type:                     {recommendation['instance_type']}\n"
            f"CPU Utilization:          {recommendation['cpu_utilization']}%\n"
            f"Action:                   {recommendation['action']}\n"
            f"Estimated Monthly Cost:   ${recommendation['estimated_monthly_cost']}\n"
            f"Estimated Monthly Saving: ${recommendation['estimated_monthly_savings']}\n"
            f"Reason:                   {recommendation['reason']}\n"
            f"{'-' * 60}"
        )

    # Step 6: Display total savings
    print(
        f"\nTOTAL ESTIMATED MONTHLY SAVINGS: "
        f"${total_savings:.2f}"
    )

    # Step 7: Save recommendations to DynamoDB
    save_recommendations(recommendations)

    print(
        f"Saved {len(recommendations)} recommendation(s) "
        f"to DynamoDB."
    )

    # Step 8: Format Telegram alert
    telegram_message = format_recommendation_alert(
        recommendations
    )

    # Step 9: Send Telegram alert
    send_message(telegram_message)

    print("Telegram alert sent successfully.")


if __name__ == "__main__":
    main()
