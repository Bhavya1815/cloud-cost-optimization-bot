from .config import IDLE_CPU_THRESHOLD
from .providers.metrics import get_metrics_provider


def is_idle(cpu_utilization):
    if cpu_utilization is None:
        return False

    return cpu_utilization < IDLE_CPU_THRESHOLD


def analyze_idle_instances(instances):
    provider = get_metrics_provider()

    results = []

    for instance in instances:
        if instance["state"] != "running":
            continue

        cpu_utilization = provider.get_cpu_utilization(
            instance["instance_id"],
            instance.get("name"),
        )

        result = instance.copy()

        result["cpu_utilization"] = (
            cpu_utilization
        )

        result["idle"] = is_idle(
            cpu_utilization
        )

        if cpu_utilization is None:
            result["metric_source"] = (
                f"{provider.source_name}_NO_DATA"
            )
        else:
            result["metric_source"] = (
                provider.source_name
            )

        results.append(result)

    return results
