import os


AWS_ENDPOINT_URL = (
    os.getenv(
        "AWS_ENDPOINT_URL",
        "http://localhost:4566",
    ).strip()
    or None
)

AWS_PROFILE = (
    os.getenv(
        "AWS_PROFILE",
        "",
    ).strip()
    or None
)

AWS_REGION = os.getenv(
    "AWS_REGION",
    "us-east-1",
)


METRICS_PROVIDER = os.getenv(
    "METRICS_PROVIDER",
    "simulated",
).lower()

PRICING_PROVIDER = os.getenv(
    "PRICING_PROVIDER",
    "simulated",
).lower()


CLOUDWATCH_ENDPOINT_URL = (
    os.getenv(
        "CLOUDWATCH_ENDPOINT_URL",
        "",
    ).strip()
    or None
)

COST_EXPLORER_ENDPOINT_URL = (
    os.getenv(
        "COST_EXPLORER_ENDPOINT_URL",
        "",
    ).strip()
    or None
)

COST_EXPLORER_REGION = os.getenv(
    "COST_EXPLORER_REGION",
    "us-east-1",
)

COST_EXPLORER_LOOKBACK_DAYS = int(
    os.getenv(
        "COST_EXPLORER_LOOKBACK_DAYS",
        "14",
    )
)

ESTIMATED_DAYS_PER_MONTH = float(
    os.getenv(
        "ESTIMATED_DAYS_PER_MONTH",
        "30.44",
    )
)


SIMULATED_HOURLY_RATES = {
    "t2.micro": 0.0116,
    "t3.micro": 0.0104,
    "t3.small": 0.0208,
    "t3.medium": 0.0416,
    "m5.large": 0.096,
}


HOURS_PER_MONTH = 730

IDLE_CPU_THRESHOLD = 10.0
