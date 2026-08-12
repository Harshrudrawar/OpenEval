from openeval.infrastructure.pricing import (
    estimate_cost,
    get_pricing,
)


def test_openai_gpt4o_pricing_is_available() -> None:
    pricing = get_pricing(
        "openai",
        "gpt-4o",
    )

    assert pricing is not None
    assert pricing.input_per_million == 2.50
    assert pricing.output_per_million == 10.00
    assert pricing.currency == "USD"


def test_estimate_cost_for_openai_gpt4o() -> None:
    cost = estimate_cost(
        "openai",
        "gpt-4o",
        input_tokens=1_000,
        output_tokens=500,
    )

    assert cost == 0.0075


def test_unknown_pricing_returns_none() -> None:
    cost = estimate_cost(
        "unknown",
        "unknown",
        input_tokens=1_000,
        output_tokens=500,
    )

    assert cost is None


def test_ollama_has_no_metered_api_cost() -> None:
    cost = estimate_cost(
        "ollama",
        "llama3",
        input_tokens=1_000,
        output_tokens=500,
    )

    assert cost is None
