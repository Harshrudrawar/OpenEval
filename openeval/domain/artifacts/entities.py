from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from openeval.domain.shared import Entity, ValidationError


@dataclass(eq=False)
class Artifact(Entity):
    """
    Represents an output artifact produced by an evaluation run.
    """

    run_id: str
    kind: str
    uri: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.run_id.strip():
            raise ValidationError("Artifact.run_id cannot be empty")

        if not self.kind.strip():
            raise ValidationError("Artifact.kind cannot be empty")

        if not self.uri.strip():
            raise ValidationError("Artifact.uri cannot be empty")