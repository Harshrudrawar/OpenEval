from __future__ import annotations

from dataclasses import dataclass

from openeval.application.ports import TargetExecutor
from openeval.domain.cases import Case, CaseResult
from openeval.domain.shared import generate_id


@dataclass
class ExecuteCasesUseCase:
    target_executor: TargetExecutor

    def execute(
        self,
        cases: list[Case],
        run_id: str,
    ) -> list[CaseResult]:
        results: list[CaseResult] = []

        for case in cases:
            try:
                raw_output = self.target_executor.execute(case)

                result = CaseResult(
                    id=generate_id(),
                    case_id=case.id,
                    run_id=run_id,
                    actual_output=raw_output,
                    status="completed",
                    metadata={
                        "expected_output": (case.expected_output or {}),
                    },
                )
            except Exception as exc:
                result = CaseResult(
                    id=generate_id(),
                    case_id=case.id,
                    run_id=run_id,
                    actual_output={},
                    status="failed",
                    metadata={
                        "expected_output": (case.expected_output or {}),
                        "error_type": type(exc).__name__,
                        "error_message": str(exc),
                    },
                )

            results.append(result)

        return results
