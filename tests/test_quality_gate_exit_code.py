from __future__ import annotations

from pathlib import Path

from openeval.interface.cli import run_from_yaml


def test_run_from_yaml_returns_one_when_quality_gate_fails(tmp_path: Path) -> None:
    dataset_file = tmp_path / "dataset.csv"
    dataset_file.write_text(
        "input,expected_output\n" '"Hello","Hi"\n',
        encoding="utf-8",
    )

    yaml_file = tmp_path / "evaluation.yaml"
    yaml_file.write_text(
        """
name: Demo Evaluation

dataset:
  version: dataset-v1
  path: {dataset_path}

prompt:
  version: prompt-v1

target:
  provider: mock

metrics:
  - accuracy

gate:
  accuracy: 1.10
""".strip().format(dataset_path=dataset_file.as_posix()),
        encoding="utf-8",
    )

    exit_code = run_from_yaml(str(yaml_file))

    assert exit_code == 1
