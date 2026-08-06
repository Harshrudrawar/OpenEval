from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from openeval.domain.shared import Entity, ValidationError


@dataclass(eq=False)
class Score(Entity):
    """
    Represents a metric score for a case or a run.
    """

    name: str
    value: float
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValidationError("Score.name cannot be empty")


@dataclass(eq=False)
class Gate(Entity):
    """
    Represents a gating rule used to decide pass/fail.
    """

    metric_name: str
    operator: str
    threshold: float
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.metric_name.strip():
            raise ValidationError("Gate.metric_name cannot be empty")

        if not self.operator.strip():
            raise ValidationError("Gate.operator cannot be empty")


@dataclass(eq=False)
class Baseline(Entity):
    """
    Represents a reference point used for comparison.
    """

    name: str
    reference_run_id: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValidationError("Baseline.name cannot be empty")

        if not self.reference_run_id.strip():
            raise ValidationError("Baseline.reference_run_id cannot be empty")