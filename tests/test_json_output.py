from __future__ import annotations

import json
from pathlib import Path

from openeval.interface.cli import (
    RunOutcome,
    _run_outcome_to_dict,
)
from openeval.interface.report import CostSummary, TokenUsage


def _make_outcome() -> RunOutcome:
    return RunOutcome(
        evaluation_name="JSON Output Test",
        evaluation_id="evaluation-1",
        run_id="run-1",
        provider="mock",
        model="unknown",
        metric_scores={
            "accuracy": 0.9,
            "contains": 0.8,
        },
        cases_count=3,
        case_results_count=3,
        accuracy=0.85,
        latency_ms=1234.0,
        target_usage=TokenUsage(
            input_tokens=100,
            output_tokens=50,
            total_tokens=150,
        ),
        judge_usage=TokenUsage(
            input_tokens=200,
            output_tokens=75,
            total_tokens=275,
        ),
        combined_usage=TokenUsage(
            input_tokens=300,
            output_tokens=125,
            total_tokens=425,
        ),
        costs=CostSummary(
            target_cost=0.001,
            judge_cost=0.002,
            combined_cost=0.003,
        ),
        gate_threshold=0.8,
        gate_passed=True,
        metric_gate_results={
            "accuracy": True,
        },
        operational_gate_results={
            "latency": True,
            "tokens": True,
            "cost": True,
        },
        gate_failures=[],
        run_status="completed",
        completed_cases_count=3,
        failed_cases_count=0,
        failed_cases=[],
        report_path=Path("reports/run-1.html"),
    )


def test_run_outcome_serializes_to_stable_json_shape() -> None:
    payload = _run_outcome_to_dict(_make_outcome())

    assert payload["schema_version"] == "1"
    assert payload["run_id"] == "run-1"
    assert payload["status"] == "completed"
    assert payload["overall_score"] == 0.85

    assert payload["metrics"] == {
        "accuracy": 0.9,
        "contains": 0.8,
    }

    assert payload["cases"] == {
        "total": 3,
        "completed": 3,
        "failed": 0,
    }

    assert payload["usage"] == {
        "target": {
            "input_tokens": 100,
            "output_tokens": 50,
            "total_tokens": 150,
        },
        "judge": {
            "input_tokens": 200,
            "output_tokens": 75,
            "total_tokens": 275,
        },
        "combined": {
            "input_tokens": 300,
            "output_tokens": 125,
            "total_tokens": 425,
        },
    }

    assert payload["estimated_cost_usd"] == 0.003
    assert payload["latency_ms"] == 1234.0

    assert payload["gates"] == {
        "passed": True,
        "metric_results": {
            "accuracy": True,
        },
        "operational_results": {
            "latency": True,
            "tokens": True,
            "cost": True,
        },
        "failures": [],
    }


def test_json_serialization_is_valid_json() -> None:
    payload = _run_outcome_to_dict(_make_outcome())

    encoded = json.dumps(
        payload,
        sort_keys=True,
    )

    decoded = json.loads(encoded)

    assert decoded == payload
