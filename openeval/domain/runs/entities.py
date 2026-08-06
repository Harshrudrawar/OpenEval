from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from openeval.domain.shared import Entity, ValidationError


@dataclass(eq=False)
class Run(Entity):
    """
    Represents a single evaluation execution.
    """

    evaluation_definition_id: str
    status: str = "created"
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.evaluation_definition_id.strip():
            raise ValidationError("Run.evaluation_definition_id cannot be empty")

        if not self.status.strip():
            raise ValidationError("Run.status cannot be empty")