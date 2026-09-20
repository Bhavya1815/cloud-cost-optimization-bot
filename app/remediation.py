from .aws_client import get_ec2_client


def can_stop_instance(instance):
    """
    Safety checks before allowing an EC2 instance
    to be stopped.
    """

    if instance.get("state") != "running":
        return False, "Instance is not running."

    if instance.get("environment") == "prod":
        return False, "Production instances cannot be stopped."

    if instance.get("critical") == "true":
        return False, "Critical instances cannot be stopped."

    if instance.get("cost_optimization") != "true":
        return False, (
            "Instance is not marked for cost optimization."
        )

    if not instance.get("idle", False):
        return False, "Instance is not currently idle."

    return True, "Instance passed all safety checks."


def stop_instance(instance):
    """
    Stop an EC2 instance after safety validation.
    """

    allowed, reason = can_stop_instance(instance)

    if not allowed:
        return {
            "success": False,
            "instance_id": instance["instance_id"],
            "reason": reason,
        }

    ec2 = get_ec2_client()

    response = ec2.stop_instances(
        InstanceIds=[
            instance["instance_id"]
        ]
    )

    stopping_instances = response.get(
        "StoppingInstances",
        []
    )

    if stopping_instances:
        return {
            "success": True,
            "instance_id": instance["instance_id"],
            "reason": "Instance stop request submitted.",
        }

    return {
        "success": False,
        "instance_id": instance["instance_id"],
        "reason": "EC2 stop request returned no instances.",
    }
