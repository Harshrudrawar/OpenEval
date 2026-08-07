from __future__ import annotations

from typing import Any

from openeval.application.ports import TargetExecutor


class MockTargetExecutor(TargetExecutor):
    def execute(self, case: Any) -> dict[str, Any]:
        expected_output = getattr(case, "expected_output", {}) or {}
        return {
            "output": expected_output,
            "status": "ok",
        }
