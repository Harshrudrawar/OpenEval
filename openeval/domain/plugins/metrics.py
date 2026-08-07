from __future__ import annotations

from abc import abstractmethod
from typing import Any

from .base import Plugin


class MetricPlugin(Plugin):
    @abstractmethod
    def evaluate(
        self,
        expected_output: dict[str, Any],
        actual_output: dict[str, Any],
    ) -> float:
        raise NotImplementedError

    def plugin_type(self) -> str:
        return "metric"

    def as_dict(self) -> dict[str, Any]:
        return {"name": self.name, "type": self.plugin_type()}
