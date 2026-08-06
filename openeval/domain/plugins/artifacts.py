from __future__ import annotations

from typing import Any

from .base import Plugin


class ArtifactPlugin(Plugin):
    """
    Base class for artifact kind plugins.
    """

    def plugin_type(self) -> str:
        return "artifact"

    def as_dict(self) -> dict[str, Any]:
        return {"name": self.name, "type": self.plugin_type()}
