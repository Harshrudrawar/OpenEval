from __future__ import annotations

from openeval.infrastructure.metric_plugins import AccuracyMetricPlugin


def test_accuracy_metric_plugin_returns_one_for_exact_match() -> None:
    plugin = AccuracyMetricPlugin()

    score = plugin.evaluate(
        expected_output={"expected_output": "Hi"},
        actual_output={"output": {"expected_output": "Hi"}},
    )

    assert score == 1.0


def test_accuracy_metric_plugin_returns_zero_for_mismatch() -> None:
    plugin = AccuracyMetricPlugin()

    score = plugin.evaluate(
        expected_output={"expected_output": "Hi"},
        actual_output={"output": {"expected_output": "Hello"}},
    )

    assert score == 0.0
