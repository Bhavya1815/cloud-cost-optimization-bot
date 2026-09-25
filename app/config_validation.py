import os


def validate_configuration():
    metrics_provider = os.getenv(
        "METRICS_PROVIDER",
        "simulated",
    ).lower()

    pricing_provider = os.getenv(
        "PRICING_PROVIDER",
        "simulated",
    ).lower()

    if metrics_provider not in {
        "simulated",
        "cloudwatch",
    }:
        raise ValueError(
            "Invalid METRICS_PROVIDER: "
            f"{metrics_provider}"
        )

    if pricing_provider not in {
        "simulated",
        "cost_explorer",
    }:
        raise ValueError(
            "Invalid PRICING_PROVIDER: "
            f"{pricing_provider}"
        )

    aws_endpoint = os.getenv(
        "AWS_ENDPOINT_URL",
        "",
    ).strip()

    # Prevent accidental use of real AWS from the
    # local Floci environment when simulated providers
    # are selected explicitly.
    if (
        metrics_provider == "simulated"
        and pricing_provider == "simulated"
        and not aws_endpoint
    ):
        return

    return