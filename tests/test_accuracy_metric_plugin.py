from __future__ import annotations

import pytest

from openeval.infrastructure.metric_plugins import (
    AccuracyMetricPlugin,
    ContainsMetricPlugin,
    OllamaJudgeMetricPlugin,
    build_metric_plugin,
)


def test_accuracy_metric_plugin_returns_one_for_matching_output() -> None:
    plugin = AccuracyMetricPlugin()

    score = plugin.evaluate(
        expected_output={"answer": "Paris"},
        actual_output={"output": {"answer": "Paris"}},
    )

    assert score == 1.0


def test_accuracy_metric_plugin_returns_zero_for_different_output() -> None:
    plugin = AccuracyMetricPlugin()

    score = plugin.evaluate(
        expected_output={"answer": "Paris"},
        actual_output={"output": {"answer": "London"}},
    )

    assert score == 0.0


def test_contains_metric_plugin_returns_one_for_contained_short_answer() -> None:
    plugin = ContainsMetricPlugin()

    score = plugin.evaluate(
        expected_output={"expected_output": "Paris"},
        actual_output={"output": {"response": "The capital of France is Paris."}},
    )

    assert score == 1.0


def test_contains_metric_plugin_returns_zero_when_expected_is_missing() -> None:
    plugin = ContainsMetricPlugin()

    score = plugin.evaluate(
        expected_output={"expected_output": "Berlin"},
        actual_output={"output": {"response": "The capital of France is Paris."}},
    )

    assert score == 0.0


def test_build_metric_plugin_returns_accuracy_plugin() -> None:
    plugin = build_metric_plugin("accuracy")

    assert isinstance(plugin, AccuracyMetricPlugin)
    assert plugin.name == "accuracy"


def test_build_metric_plugin_returns_contains_plugin() -> None:
    plugin = build_metric_plugin("contains")

    assert isinstance(plugin, ContainsMetricPlugin)
    assert plugin.name == "contains"


def test_build_metric_plugin_returns_ollama_judge_plugin() -> None:
    plugin = build_metric_plugin(
        "llm_judge",
        {"provider": "ollama", "model": "llama3"},
    )

    assert isinstance(plugin, OllamaJudgeMetricPlugin)
    assert plugin.name == "llm_judge"
    assert plugin.model == "llama3"
    assert plugin.base_url == "http://localhost:11434/api"


def test_build_metric_plugin_raises_for_unsupported_metric() -> None:
    with pytest.raises(ValueError, match="Unsupported metric plugin"):
        build_metric_plugin("bleu")
