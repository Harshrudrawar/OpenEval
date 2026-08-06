from __future__ import annotations

from abc import ABC
from dataclasses import dataclass


@dataclass(eq=False)
class Entity(ABC):
    """
    Base class for all domain entities.

    Entities are compared by identity rather than value.
    """

    id: str

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Entity):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
