from pathlib import Path

import pytest

from openeval.interface.cli import (
    _evaluate_gates,
    _load_inputs,
)


def test_metric_gate_passes_when_metric_meets_threshold() -> None:
    (
        overall_threshold,
        overall_passed,
        metric_results,
        operational_results,
        failures,
    ) = _evaluate_gates(
        overall_score=0.90,
        metric_scores={"llm_judge": 0.85},
        gate_config={
            "overall": 0.80,
            "metrics": {
                "llm_judge": 0.80,
            },
        },
    )

    assert overall_threshold == 0.80
    assert overall_passed is True
    assert metric_results == {"llm_judge": True}
    assert operational_results == {}
    assert failures == []


def test_metric_gate_fails_when_metric_is_below_threshold() -> None:
    (
        overall_threshold,
        overall_passed,
        metric_results,
        operational_results,
        failures,
    ) = _evaluate_gates(
        overall_score=0.90,
        metric_scores={"llm_judge": 0.72},
        gate_config={
            "overall": 0.80,
            "metrics": {
                "llm_judge": 0.80,
            },
        },
    )

    assert overall_threshold == 0.80
    assert overall_passed is False
    assert metric_results == {"llm_judge": False}
    assert operational_results == {}
    assert failures == ["metric:llm_judge"]


def test_metric_gate_fails_when_metric_is_missing() -> None:
    (
        _,
        overall_passed,
        metric_results,
        operational_results,
        failures,
    ) = _evaluate_gates(
        overall_score=0.90,
        metric_scores={},
        gate_config={
            "metrics": {
                "llm_judge": 0.80,
            },
        },
    )

    assert overall_passed is False
    assert metric_results == {"llm_judge": False}
    assert operational_results == {}
    assert failures == ["metric:llm_judge"]


def test_legacy_accuracy_gate_still_works() -> None:
    (
        overall_threshold,
        overall_passed,
        metric_results,
        operational_results,
        failures,
    ) = _evaluate_gates(
        overall_score=0.85,
        metric_scores={},
        gate_config={
            "accuracy": 0.80,
        },
    )

    assert overall_threshold == 0.80
    assert overall_passed is True
    assert metric_results == {}
    assert operational_results == {}
    assert failures == []


def test_gate_metrics_must_be_mapping() -> None:
    with pytest.raises(
        ValueError,
        match="gate.metrics must be a YAML mapping/object",
    ):
        _evaluate_gates(
            overall_score=0.90,
            metric_scores={"accuracy": 1.0},
            gate_config={
                "metrics": ["accuracy"],
            },
        )


def test_gate_metric_threshold_must_be_numeric() -> None:
    with pytest.raises(
        ValueError,
        match="gate metric threshold for accuracy must be a number",
    ):
        _evaluate_gates(
            overall_score=0.90,
            metric_scores={"accuracy": 1.0},
            gate_config={
                "metrics": {
                    "accuracy": "high",
                },
            },
        )


def test_metric_gate_configuration_is_loaded_from_yaml(
    tmp_path: Path,
) -> None:
    dataset_file = tmp_path / "dataset.csv"
    dataset_file.write_text(
        "input,expected_output\n" '"Hello","Hi"\n',
        encoding="utf-8",
    )

    yaml_file = tmp_path / "evaluation.yaml"
    yaml_file.write_text(
        f"""
name: Metric Gates

dataset:
  version: dataset-v1
  path: {dataset_file.as_posix()}

prompt:
  version: prompt-v1

target:
  provider: mock

metrics:
  - name: accuracy
    weight: 0.5
  - name: contains
    weight: 0.5

gate:
  overall: 0.85
  metrics:
    accuracy: 0.90
    contains: 0.80
""".strip(),
        encoding="utf-8",
    )

    inputs = _load_inputs(str(yaml_file))

    assert inputs.gate_config == {
        "overall": 0.85,
        "metrics": {
            "accuracy": 0.90,
            "contains": 0.80,
        },
    }
