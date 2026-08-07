from __future__ import annotations

from openeval.infrastructure.metric_plugins import (
    AccuracyMetricPlugin,
    ContainsMetricPlugin,
    build_metric_plugin,
)


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


def test_accuracy_metric_plugin_returns_one_for_contained_short_answer() -> None:
    plugin = ContainsMetricPlugin()

    score = plugin.evaluate(
        expected_output={"expected_output": "Paris"},
        actual_output={"output": {"response": "The capital of France is Paris."}},
    )

    assert score == 1.0


def test_build_metric_plugin_returns_contains_plugin() -> None:
    plugin = build_metric_plugin("contains")

    assert isinstance(plugin, ContainsMetricPlugin)
