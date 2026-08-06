from __future__ import annotations

from dataclasses import dataclass

from openeval.domain.runs import Run
from openeval.domain.shared import generate_id


@dataclass
class CreateRunUseCase:
    run_repository: object

    def execute(self, evaluation_definition_id: str) -> Run:
        run = Run(
            id=generate_id(),
            evaluation_definition_id=evaluation_definition_id,
            status="created",
        )

        self.run_repository.save(run)

        return run
