from datetime import datetime, timedelta, timezone
from typing import Optional

import boto3

from ..config import (
    AWS_REGION,
    CLOUDWATCH_ENDPOINT_URL,
    METRICS_PROVIDER,
)


SIMULATED_CPU_UTILIZATION = {
    "dev-idle-01": 6.55,
    "dev-idle-02": 17.79,
    "dev-idle-03": 4.25,
    "dev-active-01": 65.00,
    "production-idle-01": 3.50,
    "dev-critical-01": 2.50,
    "dev-no-opt-01": 1.50,
    "production-01": 21.46,
}


class MetricsProvider:
    source_name = "UNKNOWN"

    def get_cpu_utilization(
        self,
        instance_id: str,
        instance_name: Optional[str] = None,
    ):
        raise NotImplementedError


class SimulatedMetricsProvider(MetricsProvider):
    source_name = "SIMULATED"

    def get_cpu_utilization(
        self,
        instance_id: str,
        instance_name: Optional[str] = None,
    ):
        if instance_name in SIMULATED_CPU_UTILIZATION:
            return SIMULATED_CPU_UTILIZATION[
                instance_name
            ]

        if instance_id in SIMULATED_CPU_UTILIZATION:
            return SIMULATED_CPU_UTILIZATION[
                instance_id
            ]

        # Unknown resources are deliberately treated
        # as active during local testing.
        return 50.0


class CloudWatchMetricsProvider(MetricsProvider):
    source_name = "CLOUDWATCH"

    def __init__(self):
        client_kwargs = {
            "region_name": AWS_REGION,
        }

        if CLOUDWATCH_ENDPOINT_URL:
            client_kwargs["endpoint_url"] = (
                CLOUDWATCH_ENDPOINT_URL
            )

        session = boto3.Session(
            region_name=AWS_REGION,
        )

        self.cloudwatch = session.client(
            "cloudwatch",
            **client_kwargs,
        )

    def get_cpu_utilization(
        self,
        instance_id: str,
        instance_name: Optional[str] = None,
    ):
        end_time = datetime.now(timezone.utc)

        start_time = (
            end_time
            - timedelta(hours=1)
        )

        response = self.cloudwatch.get_metric_data(
            MetricDataQueries=[
                {
                    "Id": "cpu",
                    "ReturnData": True,
                    "MetricStat": {
                        "Metric": {
                            "Namespace": "AWS/EC2",
                            "MetricName": "CPUUtilization",
                            "Dimensions": [
                                {
                                    "Name": "InstanceId",
                                    "Value": instance_id,
                                }
                            ],
                        },
                        "Period": 300,
                        "Stat": "Average",
                        "Unit": "Percent",
                    },
                }
            ],
            StartTime=start_time,
            EndTime=end_time,
            ScanBy="TimestampDescending",
        )

        results = response.get(
            "MetricDataResults",
            [],
        )

        if not results:
            return None

        result = results[0]

        values = result.get(
            "Values",
            [],
        )

        timestamps = result.get(
            "Timestamps",
            [],
        )

        if not values or not timestamps:
            return None

        latest_value = max(
            zip(timestamps, values),
            key=lambda item: item[0],
        )[1]

        return round(
            float(latest_value),
            2,
        )


def get_metrics_provider():
    if METRICS_PROVIDER == "simulated":
        return SimulatedMetricsProvider()

    if METRICS_PROVIDER == "cloudwatch":
        return CloudWatchMetricsProvider()

    raise ValueError(
        "Unsupported METRICS_PROVIDER: "
        f"{METRICS_PROVIDER}. "
        "Supported values: simulated, cloudwatch."
    )
