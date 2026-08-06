from __future__ import annotations

from typing import Any

from .base import Plugin


class TargetPlugin(Plugin):
    """
    Base class for target plugins.
    """

    def plugin_type(self) -> str:
        return "target"

    def as_dict(self) -> dict[str, Any]:
        return {"name": self.name, "type": self.plugin_type()}