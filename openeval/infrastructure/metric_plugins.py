from __future__ import annotations

from typing import Any

from openeval.domain.plugins import MetricPlugin


def _normalize(value: Any) -> Any:
    if isinstance(value, str):
        return value.strip().casefold()
    if isinstance(value, dict):
        return {str(key): _normalize(inner_value) for key, inner_value in value.items()}
    if isinstance(value, list):
        return [_normalize(item) for item in value]
    return value


class AccuracyMetricPlugin(MetricPlugin):
    name = "accuracy"

    def evaluate(
        self,
        expected_output: dict[str, Any],
        actual_output: dict[str, Any],
    ) -> float:
        returned_output = actual_output.get("output", {})
        return (
            1.0 if _normalize(expected_output) == _normalize(returned_output) else 0.0
        )
