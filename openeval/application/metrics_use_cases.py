from __future__ import annotations

from dataclasses import dataclass

from openeval.domain.cases import CaseResult
from openeval.domain.plugins import MetricPlugin
from openeval.domain.scoring import Score
from openeval.domain.shared import ValidationError, generate_id


@dataclass
class EvaluateCaseResultsUseCase:
    metric_plugins: MetricPlugin | list[MetricPlugin]

    def _resolve_metric_plugins(self) -> list[MetricPlugin]:
        if isinstance(self.metric_plugins, list):
            plugins = self.metric_plugins
        else:
            plugins = [self.metric_plugins]

        if not plugins:
            raise ValidationError("metric_plugins must not be empty")

        return plugins

    def execute(
        self,
        cases: list[CaseResult],
        case_results: list[CaseResult],
    ) -> list[Score]:
        if len(cases) != len(case_results):
            raise ValidationError("cases and case_results must have the same length")

        scores: list[Score] = []
        plugins = self._resolve_metric_plugins()

        for metric_plugin in plugins:
            for case_result in case_results:
                expected_output = case_result.metadata.get("expected_output", {})
                score_value = metric_plugin.evaluate(
                    expected_output=expected_output,
                    actual_output=case_result.actual_output,
                )
                scores.append(
                    Score(
                        id=generate_id(),
                        name=metric_plugin.name,
                        value=score_value,
                    )
                )

        return scores
