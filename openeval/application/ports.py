from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class EvaluationRepository(ABC):
    @abstractmethod
    def save(self, evaluation: Any) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, evaluation_id: str) -> Any | None:
        raise NotImplementedError


class DatasetRepository(ABC):
    @abstractmethod
    def save(self, dataset: Any) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, dataset_id: str) -> Any | None:
        raise NotImplementedError


class PromptRepository(ABC):
    @abstractmethod
    def save(self, prompt: Any) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, prompt_id: str) -> Any | None:
        raise NotImplementedError


class RunRepository(ABC):
    @abstractmethod
    def save(self, run: Any) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, run_id: str) -> Any | None:
        raise NotImplementedError
