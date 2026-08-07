from __future__ import annotations

from openeval.domain.cases import Case
from openeval.infrastructure.target_executors import MockTargetExecutor


def test_mock_target_executor_returns_output() -> None:
    case = Case(
        id="case-1",
        evaluation_definition_id="eval-1",
        input_data={"input": "Hello"},
        expected_output={"expected_output": "Hi"},
    )

    executor = MockTargetExecutor()
    output = executor.execute(case)

    assert output["status"] == "ok"
    assert output["output"] == {"input": "Hello"}
