from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from openeval.domain.shared import Entity, ValidationError


@dataclass(eq=False)
class EvaluationDefinition(Entity):
    """
    Defines what OpenEval will evaluate.

    This is the aggregate root for a single evaluation configuration.
    """

    name: str
    dataset_version_id: str
    prompt_version_id: str
    target: dict[str, Any]
    metric_plugins: list[dict[str, Any]] = field(default_factory=list)
    gate: dict[str, Any] | None = None
    baseline: dict[str, Any] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValidationError("EvaluationDefinition.name cannot be empty")

        if not self.dataset_version_id.strip():
            raise ValidationError(
                "EvaluationDefinition.dataset_version_id cannot be empty"
            )

        if not self.prompt_version_id.strip():
            raise ValidationError(
                "EvaluationDefinition.prompt_version_id cannot be empty"
            )

        if not isinstance(self.target, dict) or not self.target:
            raise ValidationError(
                "EvaluationDefinition.target must be a non-empty dict"
            )

        if not self.metric_plugins:
            raise ValidationError(
                "EvaluationDefinition.metric_plugins must contain at least one metric"
            )