from __future__ import annotations

import re
from typing import Any

from openeval.domain.plugins import MetricPlugin


def _normalize_structure(value: Any) -> Any:
    if isinstance(value, str):
        return value.strip().casefold()
    if isinstance(value, dict):
        return {
            str(key): _normalize_structure(inner_value)
            for key, inner_value in value.items()
        }
    if isinstance(value, list):
        return [_normalize_structure(item) for item in value]
    return value


def _flatten_text(value: Any) -> str:
    if isinstance(value, str):
        return value.strip().casefold()
    if isinstance(value, dict):
        parts = [_flatten_text(inner_value) for inner_value in value.values()]
        return " ".join(part for part in parts if part).strip()
    if isinstance(value, list):
        parts = [_flatten_text(item) for item in value]
        return " ".join(part for part in parts if part).strip()
    if value is None:
        return ""
    return str(value).strip().casefold()


def _contains_expected(expected_text: str, actual_text: str) -> bool:
    if not expected_text or not actual_text:
        return False

    pattern = rf"\b{re.escape(expected_text)}\b"
    return re.search(pattern, actual_text) is not None


class AccuracyMetricPlugin(MetricPlugin):
    name = "accuracy"

    def evaluate(
        self,
        expected_output: dict[str, Any],
        actual_output: dict[str, Any],
    ) -> float:
        returned_output = actual_output.get("output", {})

        if _normalize_structure(expected_output) == _normalize_structure(
            returned_output
        ):
            return 1.0

        expected_text = _flatten_text(expected_output)
        actual_text = _flatten_text(returned_output)

        return 1.0 if _contains_expected(expected_text, actual_text) else 0.0
