from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from openeval.domain.shared import Entity, ValidationError


@dataclass(eq=False)
class Case(Entity):
    """
    Represents one test case inside an evaluation.
    """

    evaluation_definition_id: str
    input_data: dict[str, Any]
    expected_output: dict[str, Any] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.evaluation_definition_id.strip():
            raise ValidationError("Case.evaluation_definition_id cannot be empty")

        if not isinstance(self.input_data, dict) or not self.input_data:
            raise ValidationError("Case.input_data must be a non-empty dict")


@dataclass(eq=False)
class CaseResult(Entity):
    """
    Represents the output of running a single case.
    """

    case_id: str
    run_id: str
    actual_output: dict[str, Any]
    status: str = "pending"
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.case_id.strip():
            raise ValidationError("CaseResult.case_id cannot be empty")

        if not self.run_id.strip():
            raise ValidationError("CaseResult.run_id cannot be empty")

        if not isinstance(self.actual_output, dict):
            raise ValidationError("CaseResult.actual_output must be a dict")

        if not self.status.strip():
            raise ValidationError("CaseResult.status cannot be empty")
