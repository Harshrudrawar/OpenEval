from __future__ import annotations

from pathlib import Path
from typing import Any

import openeval.interface.cli as cli


class PartiallyFailingTargetExecutor:
    def __init__(self) -> None:
        self.call_count = 0

    def execute(self, case: Any) -> dict[str, Any]:
        self.call_count += 1

        if self.call_count == 2:
            raise RuntimeError("simulated provider failure")

        return {
            "output": (getattr(case, "expected_output", None) or {}),
            "status": "ok",
        }


def test_failed_case_causes_failed_run_and_nonzero_exit(
    tmp_path: Path,
    monkeypatch: Any,
) -> None:
    dataset_path = tmp_path / "dataset.csv"
    dataset_path.write_text(
        "input,expected_output\n" '"one","one"\n' '"two","two"\n' '"three","three"\n',
        encoding="utf-8",
    )

    config_path = tmp_path / "evaluation.yaml"
    config_path.write_text(
        f"""
name: Failure Resilience Test

dataset:
  version: dataset-v1
  path: {dataset_path.as_posix()}

prompt:
  version: prompt-v1

target:
  provider: mock

metrics:
  - accuracy
""".strip(),
        encoding="utf-8",
    )

    executor = PartiallyFailingTargetExecutor()

    monkeypatch.setattr(
        cli,
        "build_target_executor",
        lambda target: executor,
    )

    monkeypatch.chdir(tmp_path)

    exit_code = cli.run_from_yaml(str(config_path))

    assert exit_code == 1
    assert executor.call_count == 3

    reports_dir = tmp_path / "reports"

    assert reports_dir.exists()

    html_reports = list(reports_dir.glob("*.html"))

    assert len(html_reports) == 1

    report_html = html_reports[0].read_text(encoding="utf-8")

    assert "Failure Resilience Test" in report_html

    history_path = reports_dir / "run-history.jsonl"

    assert history_path.exists()

    history_text = history_path.read_text(encoding="utf-8")

    assert '"run_status": "failed"' in history_text
    assert '"failed_cases_count": 1' in history_text
    assert '"completed_cases_count": 2' in history_text
    assert "simulated provider failure" in history_text


def test_successful_execution_produces_completed_run(
    tmp_path: Path,
    monkeypatch: Any,
) -> None:
    dataset_path = tmp_path / "dataset.csv"
    dataset_path.write_text(
        "input,expected_output\n" '"one","one"\n' '"two","two"\n',
        encoding="utf-8",
    )

    config_path = tmp_path / "evaluation.yaml"
    config_path.write_text(
        f"""
name: Successful Lifecycle Test

dataset:
  version: dataset-v1
  path: {dataset_path.as_posix()}

prompt:
  version: prompt-v1

target:
  provider: mock

metrics:
  - accuracy
""".strip(),
        encoding="utf-8",
    )

    monkeypatch.chdir(tmp_path)

    exit_code = cli.run_from_yaml(str(config_path))

    assert exit_code == 0

    history_path = tmp_path / "reports" / "run-history.jsonl"

    assert history_path.exists()

    history_text = history_path.read_text(encoding="utf-8")

    assert '"run_status": "completed"' in history_text
    assert '"failed_cases_count": 0' in history_text
    assert '"completed_cases_count": 2' in history_text
