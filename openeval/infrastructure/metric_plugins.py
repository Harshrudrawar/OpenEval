from __future__ import annotations

from typing import Any

from openeval.domain.plugins import MetricPlugin


class AccuracyMetricPlugin(MetricPlugin):
    name = "accuracy"

    def evaluate(
        self,
        expected_output: dict[str, Any],
        actual_output: dict[str, Any],
    ) -> float:
        returned_output = actual_output.get("output", {})
        return 1.0 if expected_output == returned_output else 0.0
