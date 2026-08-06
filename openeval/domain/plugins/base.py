from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Plugin(ABC):
    """
    Base class for all OpenEval plugins.
    """

    name: str

    @abstractmethod
    def plugin_type(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def as_dict(self) -> dict[str, Any]:
        raise NotImplementedError