from datetime import datetime, timedelta, timezone

import boto3

from ..config import (
    AWS_REGION,
    COST_EXPLORER_ENDPOINT_URL,
    COST_EXPLORER_LOOKBACK_DAYS,
    ESTIMATED_DAYS_PER_MONTH,
    HOURS_PER_MONTH,
    PRICING_PROVIDER,
    SIMULATED_HOURLY_RATES,
)


class PricingProvider:
    source_name = "UNKNOWN"

    def estimate_monthly_cost(
        self,
        instance_type,
        instance_id=None,
    ):
        raise NotImplementedError


class SimulatedPricingProvider(PricingProvider):
    source_name = "SIMULATED"

    def estimate_monthly_cost(
        self,
        instance_type,
        instance_id=None,
    ):
        hourly_rate = SIMULATED_HOURLY_RATES.get(
            instance_type,
            0,
        )

        return round(
            hourly_rate * HOURS_PER_MONTH,
            2,
        )


class CostExplorerPricingProvider(PricingProvider):
    source_name = "COST_EXPLORER"

    def __init__(self):
        client_kwargs = {
            "region_name": AWS_REGION,
        }

        if COST_EXPLORER_ENDPOINT_URL:
            client_kwargs["endpoint_url"] = (
                COST_EXPLORER_ENDPOINT_URL
            )

        session = boto3.Session(
            region_name=AWS_REGION,
        )

        self.cost_explorer = session.client(
            "ce",
            **client_kwargs,
        )

    def estimate_monthly_cost(
        self,
        instance_type,
        instance_id=None,
    ):
        if not instance_id:
            raise ValueError(
                "Cost Explorer pricing requires "
                "an EC2 instance ID."
            )

        end_date = datetime.now(
            timezone.utc
        ).date()

        start_date = (
            end_date
            - timedelta(
                days=COST_EXPLORER_LOOKBACK_DAYS
            )
        )

        response = self.cost_explorer.get_cost_and_usage_with_resources(
            TimePeriod={
                "Start": start_date.isoformat(),
                "End": end_date.isoformat(),
            },
            Granularity="DAILY",
            Metrics=[
                "UnblendedCost",
            ],
            Filter={
                "And": [
                    {
                        "Dimensions": {
                            "Key": "SERVICE",
                            "Values": [
                                "Amazon Elastic Compute Cloud - Compute"
                            ],
                        }
                    },
                    {
                        "Dimensions": {
                            "Key": "RESOURCE_ID",
                            "Values": [
                                instance_id
                            ],
                        }
                    },
                ]
            },
        )

        total_cost = 0.0
        observed_days = 0

        for result in response.get(
            "ResultsByTime",
            [],
        ):
            metrics = result.get(
                "Total",
                {},
            )

            unblended_cost = metrics.get(
                "UnblendedCost"
            )

            if not unblended_cost:
                continue

            total_cost += float(
                unblended_cost["Amount"]
            )

            observed_days += 1

        next_page_token = response.get(
            "NextPageToken"
        )

        while next_page_token:
            response = self.cost_explorer.get_cost_and_usage_with_resources(
                TimePeriod={
                    "Start": start_date.isoformat(),
                    "End": end_date.isoformat(),
                },
                Granularity="DAILY",
                Metrics=[
                    "UnblendedCost",
                ],
                Filter={
                    "And": [
                        {
                            "Dimensions": {
                                "Key": "SERVICE",
                                "Values": [
                                    "Amazon Elastic Compute Cloud - Compute"
                                ],
                            }
                        },
                        {
                            "Dimensions": {
                                "Key": "RESOURCE_ID",
                                "Values": [
                                    instance_id
                                ],
                            }
                        },
                    ]
                },
                NextPageToken=next_page_token,
            )

            for result in response.get(
                "ResultsByTime",
                [],
            ):
                metrics = result.get(
                    "Total",
                    {},
                )

                unblended_cost = metrics.get(
                    "UnblendedCost"
                )

                if not unblended_cost:
                    continue

                total_cost += float(
                    unblended_cost["Amount"]
                )

                observed_days += 1

            next_page_token = response.get(
                "NextPageToken"
            )

        if observed_days == 0:
            return None

        average_daily_cost = (
            total_cost / observed_days
        )

        return round(
            average_daily_cost
            * ESTIMATED_DAYS_PER_MONTH,
            2,
        )


def get_pricing_provider():
    if PRICING_PROVIDER == "simulated":
        return SimulatedPricingProvider()

    if PRICING_PROVIDER == "cost_explorer":
        return CostExplorerPricingProvider()

    raise ValueError(
        "Unsupported PRICING_PROVIDER: "
        f"{PRICING_PROVIDER}. "
        "Supported values: simulated, cost_explorer."
    )
