from pathlib import Path

import pytest

from openeval.interface.cli import (
    MetricConfig,
    _load_inputs,
    _weighted_overall_score,
)


def test_weighted_score_uses_metric_weights() -> None:
    metric_scores = {
        "accuracy": 0.0,
        "contains": 1.0,
    }

    metric_configs = [
        MetricConfig(
            name="accuracy",
            weight=0.25,
        ),
        MetricConfig(
            name="contains",
            weight=0.75,
        ),
    ]

    score = _weighted_overall_score(
        metric_scores,
        metric_configs,
    )

    assert score == pytest.approx(0.75)


def test_equal_weights_preserve_average() -> None:
    metric_scores = {
        "accuracy": 0.0,
        "contains": 1.0,
    }

    metric_configs = [
        MetricConfig(
            name="accuracy",
            weight=1.0,
        ),
        MetricConfig(
            name="contains",
            weight=1.0,
        ),
    ]

    score = _weighted_overall_score(
        metric_scores,
        metric_configs,
    )

    assert score == pytest.approx(0.5)


def test_weighted_score_handles_multiple_metrics() -> None:
    metric_scores = {
        "accuracy": 1.0,
        "contains": 0.5,
        "llm_judge": 0.0,
    }

    metric_configs = [
        MetricConfig(
            name="accuracy",
            weight=0.2,
        ),
        MetricConfig(
            name="contains",
            weight=0.3,
        ),
        MetricConfig(
            name="llm_judge",
            weight=0.5,
        ),
    ]

    score = _weighted_overall_score(
        metric_scores,
        metric_configs,
    )

    assert score == pytest.approx(0.35)


def test_legacy_metric_strings_default_to_weight_one(
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
name: Legacy Metrics

dataset:
  version: dataset-v1
  path: {dataset_file.as_posix()}

prompt:
  version: prompt-v1

target:
  provider: mock

metrics:
  - accuracy
  - contains
""".strip(),
        encoding="utf-8",
    )

    inputs = _load_inputs(str(yaml_file))

    assert inputs.metric_names == [
        "accuracy",
        "contains",
    ]

    assert [config.weight for config in inputs.metric_configs] == [1.0, 1.0]


@pytest.mark.parametrize(
    "weight",
    [
        0,
        -1,
    ],
)
def test_non_positive_metric_weight_is_rejected(
    tmp_path: Path,
    weight: int,
) -> None:
    dataset_file = tmp_path / "dataset.csv"
    dataset_file.write_text(
        "input,expected_output\n" '"Hello","Hi"\n',
        encoding="utf-8",
    )

    yaml_file = tmp_path / "evaluation.yaml"
    yaml_file.write_text(
        f"""
name: Invalid Weight

dataset:
  version: dataset-v1
  path: {dataset_file.as_posix()}

prompt:
  version: prompt-v1

target:
  provider: mock

metrics:
  - name: accuracy
    weight: {weight}
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="metric weight must be greater than 0",
    ):
        _load_inputs(str(yaml_file))
