from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Pricing:
    input_per_million: float
    output_per_million: float
    currency: str = "USD"


_PRICING: dict[tuple[str, str], Pricing] = {
    ("openai", "gpt-4o"): Pricing(
        input_per_million=2.50,
        output_per_million=10.00,
    ),
}


def get_pricing(
    provider: str,
    model: str,
) -> Pricing | None:
    key = (
        provider.strip().casefold(),
        model.strip().casefold(),
    )

    return _PRICING.get(key)


def estimate_cost(
    provider: str,
    model: str,
    *,
    input_tokens: int,
    output_tokens: int,
) -> float | None:
    pricing = get_pricing(
        provider,
        model,
    )

    if pricing is None:
        return None

    safe_input_tokens = max(
        input_tokens,
        0,
    )
    safe_output_tokens = max(
        output_tokens,
        0,
    )

    input_cost = safe_input_tokens / 1_000_000 * pricing.input_per_million

    output_cost = safe_output_tokens / 1_000_000 * pricing.output_per_million

    return input_cost + output_cost
