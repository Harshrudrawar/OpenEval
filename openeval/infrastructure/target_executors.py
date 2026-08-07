from __future__ import annotations

from typing import Any

from openeval.application.ports import TargetExecutor


class MockTargetExecutor(TargetExecutor):
    def execute(self, case: Any) -> dict[str, Any]:
        input_data = getattr(case, "input_data", {})
        return {
            "output": input_data,
            "status": "ok",
        }
