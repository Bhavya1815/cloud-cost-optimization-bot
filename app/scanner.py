from .aws_client import get_ec2_client


def get_tag(tags, key):
    """Return a tag value by key."""
    for tag in tags or []:
        if tag.get("Key") == key:
            return tag.get("Value")

    return None


def scan_ec2_instances():
    """Discover EC2 instances from Floci."""

    ec2 = get_ec2_client()

    response = ec2.describe_instances()

    resources = []

    for reservation in response.get("Reservations", []):
        for instance in reservation.get("Instances", []):

            tags = instance.get("Tags", [])

            resources.append({
                "instance_id": instance.get("InstanceId"),
                "instance_type": instance.get("InstanceType"),
                "state": instance.get("State", {}).get("Name"),
                "name": get_tag(tags, "Name"),
                "environment": get_tag(tags, "Environment"),
                "cost_optimization": get_tag(
                    tags,
                    "CostOptimization"
                ),
                "critical": get_tag(
                    tags,
                    "Critical"
                ),
            })

    return resources
