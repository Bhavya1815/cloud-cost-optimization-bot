from .config import IDLE_CPU_THRESHOLD


# Simulated CPU utilization for local Floci testing.
#
# These values are deliberately deterministic so the
# same resource always produces the same test result.
#
# This is NOT real CloudWatch data.

SIMULATED_CPU_UTILIZATION = {
    "dev-idle-01": 6.55,
    "dev-idle-02": 17.79,
    "dev-idle-03": 4.25,
    "dev-active-01": 65.00,
    "dev-critical-01": 2.50,
    "dev-no-opt-01": 1.50,
    "production-idle-01": 3.50,
    "production-01": 21.46,
}


def get_simulated_cpu_utilization(
    instance_id,
    instance_name=None
):
    """
    Return deterministic simulated CPU utilization.

    This is NOT real CloudWatch data.
    """

    if instance_name in SIMULATED_CPU_UTILIZATION:
        return SIMULATED_CPU_UTILIZATION[
            instance_name
        ]

    if instance_id in SIMULATED_CPU_UTILIZATION:
        return SIMULATED_CPU_UTILIZATION[
            instance_id
        ]

    # Unknown resources default to active so that
    # new resources are not accidentally classified
    # as idle during testing.
    return 50.0


def is_idle(cpu_utilization):
    """
    Determine whether an instance is considered idle.
    """

    return cpu_utilization < IDLE_CPU_THRESHOLD


def analyze_idle_instances(instances):
    """
    Add simulated CPU utilization and idle status
    to discovered EC2 instances.
    """

    results = []

    for instance in instances:

        if instance["state"] != "running":
            continue

        cpu_utilization = get_simulated_cpu_utilization(
            instance["instance_id"],
            instance.get("name"),
        )

        idle = is_idle(
            cpu_utilization
        )

        result = instance.copy()

        result["cpu_utilization"] = cpu_utilization
        result["idle"] = idle
        result["metric_source"] = "SIMULATED"

        results.append(result)

    return results
