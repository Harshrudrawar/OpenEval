from dataclasses import dataclass
from typing import Any

import pytest

from openeval.application.execution_use_cases import ExecuteCasesUseCase
from openeval.application.metrics_use_cases import (
    EvaluateCaseResultsUseCase,
)
from openeval.application.run_use_cases import (
    CreateRunUseCase,
    UpdateRunStatusUseCase,
)
from openeval.domain.cases import Case, CaseResult
from openeval.domain.plugins import MetricPlugin
from openeval.domain.shared import generate_id


class FailingTargetExecutor:
    def __init__(self, failing_case_ids: set[str]) -> None:
        self.failing_case_ids = failing_case_ids

    def execute(self, case: Any) -> dict[str, Any]:
        if case.id in self.failing_case_ids:
            raise RuntimeError("target execution failed")

        return {
            "output": case.expected_output or {},
            "status": "ok",
        }


class AlwaysSuccessfulTargetExecutor:
    def execute(self, case: Any) -> dict[str, Any]:
        return {
            "output": case.expected_output or {},
            "status": "ok",
        }


@dataclass
class InMemoryRunRepository:
    runs: dict[str, Any]

    def __init__(self) -> None:
        self.runs = {}

    def save(self, run: Any) -> None:
        self.runs[run.id] = run

    def get_by_id(self, run_id: str) -> Any | None:
        return self.runs.get(run_id)


class AlwaysPassMetric(MetricPlugin):
    name = "always_pass"

    def evaluate(
        self,
        expected_output: dict[str, Any],
        actual_output: dict[str, Any],
    ) -> float:
        return 1.0


def _make_case(
    expected_output: dict[str, Any],
) -> Case:
    return Case(
        id=generate_id(),
        evaluation_definition_id=generate_id(),
        input_data={"input": "hello"},
        expected_output=expected_output,
    )


def test_execution_failure_creates_failed_case_result() -> None:
    case = _make_case({"answer": "hello"})
    executor = FailingTargetExecutor(failing_case_ids={case.id})

    use_case = ExecuteCasesUseCase(executor)

    results = use_case.execute(
        [case],
        run_id=generate_id(),
    )

    assert len(results) == 1
    assert results[0].status == "failed"
    assert results[0].actual_output == {}
    assert results[0].metadata["error_type"] == "RuntimeError"
    assert results[0].metadata["error_message"] == "target execution failed"


def test_execution_continues_after_failed_case() -> None:
    failing_case = _make_case({"answer": "failed"})
    successful_case = _make_case({"answer": "success"})

    executor = FailingTargetExecutor(failing_case_ids={failing_case.id})

    use_case = ExecuteCasesUseCase(executor)

    results = use_case.execute(
        [failing_case, successful_case],
        run_id=generate_id(),
    )

    assert len(results) == 2
    assert results[0].status == "failed"
    assert results[1].status == "completed"


def test_failed_cases_are_excluded_from_metric_scoring() -> None:
    completed_result = CaseResult(
        id=generate_id(),
        case_id=generate_id(),
        run_id=generate_id(),
        actual_output={
            "output": {"answer": "hello"},
        },
        status="completed",
        metadata={
            "expected_output": {
                "answer": "hello",
            },
        },
    )

    failed_result = CaseResult(
        id=generate_id(),
        case_id=generate_id(),
        run_id=generate_id(),
        actual_output={},
        status="failed",
        metadata={
            "expected_output": {
                "answer": "hello",
            },
            "error_type": "RuntimeError",
            "error_message": "target execution failed",
        },
    )

    use_case = EvaluateCaseResultsUseCase([AlwaysPassMetric()])

    scores = use_case.execute(
        [completed_result, failed_result],
        [completed_result, failed_result],
    )

    assert len(scores) == 1
    assert scores[0].name == "always_pass"
    assert scores[0].value == 1.0


def test_run_status_transitions_from_created_to_running_to_completed() -> None:
    repository = InMemoryRunRepository()

    create_use_case = CreateRunUseCase(repository)
    update_use_case = UpdateRunStatusUseCase(repository)

    run = create_use_case.execute(generate_id())

    assert run.status == "created"

    update_use_case.execute(
        run,
        "running",
    )

    assert run.status == "running"
    assert repository.get_by_id(run.id).status == "running"

    update_use_case.execute(
        run,
        "completed",
    )

    assert run.status == "completed"
    assert repository.get_by_id(run.id).status == "completed"


def test_run_status_transitions_to_failed() -> None:
    repository = InMemoryRunRepository()

    create_use_case = CreateRunUseCase(repository)
    update_use_case = UpdateRunStatusUseCase(repository)

    run = create_use_case.execute(generate_id())

    update_use_case.execute(
        run,
        "running",
    )

    update_use_case.execute(
        run,
        "failed",
    )

    assert run.status == "failed"
    assert repository.get_by_id(run.id).status == "failed"


def test_successful_executor_produces_only_completed_results() -> None:
    cases = [
        _make_case({"answer": "one"}),
        _make_case({"answer": "two"}),
    ]

    use_case = ExecuteCasesUseCase(AlwaysSuccessfulTargetExecutor())

    results = use_case.execute(
        cases,
        run_id=generate_id(),
    )

    assert len(results) == 2
    assert all(result.status == "completed" for result in results)


def test_failed_case_preserves_expected_output_metadata() -> None:
    case = _make_case({"answer": "expected"})

    use_case = ExecuteCasesUseCase(FailingTargetExecutor(failing_case_ids={case.id}))

    results = use_case.execute(
        [case],
        run_id=generate_id(),
    )

    assert results[0].metadata["expected_output"] == {"answer": "expected"}


@pytest.mark.parametrize(
    "status",
    [
        "created",
        "running",
        "completed",
        "failed",
    ],
)
def test_update_run_status_persists_supported_statuses(
    status: str,
) -> None:
    repository = InMemoryRunRepository()

    create_use_case = CreateRunUseCase(repository)
    update_use_case = UpdateRunStatusUseCase(repository)

    run = create_use_case.execute(generate_id())

    update_use_case.execute(
        run,
        status,
    )

    persisted = repository.get_by_id(run.id)

    assert persisted is not None
    assert persisted.status == status
