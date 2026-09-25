from app.idle_detector import is_idle
from app.providers.metrics import (
    SimulatedMetricsProvider,
)
from app.providers.pricing import (
    SimulatedPricingProvider,
)


def test_simulated_metrics_provider():
    provider = SimulatedMetricsProvider()

    cpu = provider.get_cpu_utilization(
        "i-test-1",
        "dev-idle-03",
    )

    assert cpu == 4.25


def test_unknown_simulated_resource_defaults_active():
    provider = SimulatedMetricsProvider()

    cpu = provider.get_cpu_utilization(
        "i-unknown",
        "unknown-resource",
    )

    assert cpu == 50.0


def test_simulated_provider_source():
    provider = SimulatedMetricsProvider()

    assert provider.source_name == "SIMULATED"


def test_simulated_pricing_provider():
    provider = SimulatedPricingProvider()

    cost = provider.estimate_monthly_cost(
        "t2.micro",
        "i-test-1",
    )

    assert cost == 8.47


def test_unknown_instance_type_has_zero_cost():
    provider = SimulatedPricingProvider()

    cost = provider.estimate_monthly_cost(
        "unknown.type",
        "i-test-1",
    )

    assert cost == 0


def test_simulated_pricing_source():
    provider = SimulatedPricingProvider()

    assert provider.source_name == "SIMULATED"


def test_missing_cpu_data_is_not_idle():
    assert is_idle(None) is False
