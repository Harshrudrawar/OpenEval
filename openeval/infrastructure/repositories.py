from __future__ import annotations

from typing import Optional

from openeval.application.ports import EvaluationRepository
from openeval.domain.evaluation import EvaluationDefinition
from openeval.domain.runs import Run


class InMemoryEvaluationRepository(EvaluationRepository):
    def __init__(self) -> None:
        self._store: dict[str, EvaluationDefinition] = {}

    def save(self, evaluation: EvaluationDefinition) -> None:
        self._store[evaluation.id] = evaluation

    def get_by_id(self, evaluation_id: str) -> Optional[EvaluationDefinition]:
        return self._store.get(evaluation_id)


class InMemoryRunRepository:
    def __init__(self) -> None:
        self._store: dict[str, Run] = {}

    def save(self, run: Run) -> None:
        self._store[run.id] = run

    def get_by_id(self, run_id: str) -> Optional[Run]:
        return self._store.get(run_id)