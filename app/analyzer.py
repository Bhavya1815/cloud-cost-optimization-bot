def analyze_instances(instances):
    """
    Identify EC2 instances that are safe candidates
    for cost optimization based on idle status.
    """

    recommendations = []

    for instance in instances:

        # Only consider running instances
        if instance["state"] != "running":
            continue

        # Only consider instances detected as idle
        if not instance.get("idle", False):
            continue

        # Only consider resources explicitly marked
        # for cost optimization
        if instance["cost_optimization"] != "true":
            continue

        # Never recommend critical resources
        if instance["critical"] == "true":
            continue

        # Never recommend production resources
        if instance["environment"] == "prod":
            continue

        recommendations.append({
            "instance_id": instance["instance_id"],
            "name": instance["name"],
            "instance_type": instance["instance_type"],
            "cpu_utilization": instance["cpu_utilization"],
            "action": "STOP",
            "reason": (
                "Running non-production resource with "
                f"{instance['cpu_utilization']}% CPU utilization"
            ),
        })

    return recommendations
