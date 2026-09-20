import os


AWS_ENDPOINT_URL = os.getenv(
    "AWS_ENDPOINT_URL",
    "http://localhost:4566"
)

AWS_PROFILE = os.getenv(
    "AWS_PROFILE",
    "floci"
)

AWS_REGION = os.getenv(
    "AWS_REGION",
    "us-east-1"
)


# Simulated hourly rates for local Floci testing.
#
# These are demonstration values and are NOT
# real AWS billing data.

SIMULATED_HOURLY_RATES = {
    "t2.micro": 0.0116,
    "t3.micro": 0.0104,
    "t3.small": 0.0208,
    "t3.medium": 0.0416,
    "m5.large": 0.096,
}


# Average number of hours used for a monthly estimate.
HOURS_PER_MONTH = 730


# CPU utilization below this percentage
# is considered idle.
IDLE_CPU_THRESHOLD = 10.0
