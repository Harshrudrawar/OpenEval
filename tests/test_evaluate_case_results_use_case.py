from __future__ import annotations

from openeval.application.metrics_use_cases import EvaluateCaseResultsUseCase
from openeval.domain.cases import CaseResult
from openeval.infrastructure.metric_plugins import AccuracyMetricPlugin


def test_evaluate_case_results_use_case_returns_scores() -> None:
    plugin = AccuracyMetricPlugin()
    use_case = EvaluateCaseResultsUseCase(plugin)

    case_results = [
        CaseResult(
            id="result-1",
            case_id="case-1",
            run_id="run-1",
            actual_output={"output": {"expected_output": "Hi"}},
            status="completed",
            metadata={"expected_output": {"expected_output": "Hi"}},
        )
    ]

    scores = use_case.execute(case_results, case_results)

    assert len(scores) == 1
    assert scores[0].name == "accuracy"
    assert scores[0].value == 1.0
