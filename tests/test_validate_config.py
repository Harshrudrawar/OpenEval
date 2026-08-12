from pathlib import Path

from openeval.interface.cli import validate_from_yaml


def _write_valid_config(
    tmp_path: Path,
) -> Path:
    dataset_path = tmp_path / "dataset.csv"

    dataset_path.write_text(
        "input,expected_output\n" '"hello","hello"\n',
        encoding="utf-8",
    )

    config_path = tmp_path / "evaluation.yaml"

    config_path.write_text(
        f"""
name: Validation Test

dataset:
  version: dataset-v1
  path: {dataset_path.as_posix()}

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
  overall: 0.80
  metrics:
    accuracy: 0.90
    contains: 0.80

  max_latency_ms: 30000
  max_total_tokens: 5000
  max_cost_usd: 0.05
""".strip(),
        encoding="utf-8",
    )

    return config_path


def test_validate_accepts_valid_configuration(
    tmp_path: Path,
) -> None:
    config_path = _write_valid_config(tmp_path)

    assert validate_from_yaml(str(config_path)) == 0


def test_validate_rejects_unknown_metric_gate(
    tmp_path: Path,
) -> None:
    config_path = _write_valid_config(tmp_path)

    text = config_path.read_text(encoding="utf-8")

    config_path.write_text(
        text.replace(
            "    contains: 0.80",
            "    contains: 0.80\n" "    unknown_metric: 0.90",
        ),
        encoding="utf-8",
    )

    assert validate_from_yaml(str(config_path)) == 1


def test_validate_rejects_invalid_yaml_path(
    tmp_path: Path,
) -> None:
    missing_path = tmp_path / "missing.yaml"

    assert validate_from_yaml(str(missing_path)) == 1
