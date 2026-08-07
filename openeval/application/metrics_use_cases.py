from __future__ import annotations

from dataclasses import dataclass

from openeval.domain.cases import CaseResult
from openeval.domain.plugins import MetricPlugin
from openeval.domain.scoring import Score
from openeval.domain.shared import ValidationError, generate_id


@dataclass
class EvaluateCaseResultsUseCase:
    metric_plugin: MetricPlugin

    def execute(
        self,
        cases: list[CaseResult],
        case_results: list[CaseResult],
    ) -> list[Score]:
        if len(cases) != len(case_results):
            raise ValidationError("cases and case_results must have the same length")

        scores: list[Score] = []

        for case_result in case_results:
            expected_output = case_result.metadata.get("expected_output", {})
            score_value = self.metric_plugin.evaluate(
                expected_output=expected_output,
                actual_output=case_result.actual_output,
            )
            scores.append(
                Score(
                    id=generate_id(),
                    name=self.metric_plugin.name,
                    value=score_value,
                )
            )

        return scores
