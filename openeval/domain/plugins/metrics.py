from __future__ import annotations

from typing import Any

from .base import Plugin


class MetricPlugin(Plugin):
    """
    Base class for metric plugins.
    """

    def plugin_type(self) -> str:
        return "metric"

    def as_dict(self) -> dict[str, Any]:
        return {"name": self.name, "type": self.plugin_type()}
