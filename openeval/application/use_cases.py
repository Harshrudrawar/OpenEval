from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from openeval.application.ports import EvaluationRepository
from openeval.domain.evaluation import EvaluationDefinition
from openeval.domain.shared import generate_id


@dataclass
class CreateEvaluationDefinitionUseCase:
    evaluation_repository: EvaluationRepository

    def execute(
        self,
        *,
        name: str,
        dataset_version_id: str,
        prompt_version_id: str,
        target: dict[str, Any],
        metric_plugins: list[dict[str, Any]],
        gate: dict[str, Any] | None = None,
        baseline: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> EvaluationDefinition:
        evaluation = EvaluationDefinition(
            id=generate_id(),
            name=name,
            dataset_version_id=dataset_version_id,
            prompt_version_id=prompt_version_id,
            target=target,
            metric_plugins=metric_plugins,
            gate=gate,
            baseline=baseline,
            metadata=metadata or {},
        )

        self.evaluation_repository.save(evaluation)
        return evaluation
