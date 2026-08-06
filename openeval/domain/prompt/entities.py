from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from openeval.domain.shared import Entity, ValidationError


@dataclass(eq=False)
class Prompt(Entity):
    """
    Logical prompt container.

    A Prompt groups versions over time.
    """

    name: str
    description: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValidationError("Prompt.name cannot be empty")


@dataclass(eq=False)
class PromptVersion(Entity):
    """
    Immutable version of a prompt.

    EvaluationDefinition should point to a specific version.
    """

    prompt_id: str
    version: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.prompt_id.strip():
            raise ValidationError("PromptVersion.prompt_id cannot be empty")

        if not self.version.strip():
            raise ValidationError("PromptVersion.version cannot be empty")

        if not self.content.strip():
            raise ValidationError("PromptVersion.content cannot be empty")