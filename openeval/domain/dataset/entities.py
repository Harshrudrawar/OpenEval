from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from openeval.domain.shared import Entity, ValidationError


@dataclass(eq=False)
class Dataset(Entity):
    """
    Logical dataset container.

    A Dataset groups versions over time.
    """

    name: str
    description: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValidationError("Dataset.name cannot be empty")


@dataclass(eq=False)
class DatasetVersion(Entity):
    """
    Immutable version of a dataset.

    EvaluationDefinition should point to a specific version.
    """

    dataset_id: str
    version: str
    source: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.dataset_id.strip():
            raise ValidationError("DatasetVersion.dataset_id cannot be empty")

        if not self.version.strip():
            raise ValidationError("DatasetVersion.version cannot be empty")

        if not isinstance(self.source, dict) or not self.source:
            raise ValidationError("DatasetVersion.source must be a non-empty dict")