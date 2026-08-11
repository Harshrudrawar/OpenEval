from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any

from openai import OpenAI

from openeval.application.ports import TargetExecutor


@dataclass
class OpenAITargetExecutor(TargetExecutor):
    model: str
    api_key: str | None = None
    _client: Any = field(init=False, repr=False)

    def __post_init__(self) -> None:
        key = self.api_key or os.getenv("OPENAI_API_KEY")
        if not key:
            raise RuntimeError("OPENAI_API_KEY is required for OpenAITargetExecutor")

        self._client = OpenAI(api_key=key)

    def execute(self, case: Any) -> dict[str, Any]:
        input_data = getattr(case, "input_data", {})
        prompt = self._build_prompt(input_data)

        response = self._client.responses.create(
            model=self.model,
            input=prompt,
        )

        text = getattr(response, "output_text", "")
        usage = self._extract_usage(response)

        return {
            "output": {"response": text},
            "status": "ok",
            "model": self.model,
            "usage": usage,
        }

    @staticmethod
    def _extract_usage(response: Any) -> dict[str, int]:
        usage = getattr(response, "usage", None)

        if usage is None:
            return {
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
            }

        input_tokens = getattr(usage, "input_tokens", 0)
        output_tokens = getattr(usage, "output_tokens", 0)
        total_tokens = getattr(usage, "total_tokens", 0)

        return {
            "input_tokens": (int(input_tokens) if isinstance(input_tokens, int) else 0),
            "output_tokens": (
                int(output_tokens) if isinstance(output_tokens, int) else 0
            ),
            "total_tokens": (int(total_tokens) if isinstance(total_tokens, int) else 0),
        }

    def _build_prompt(self, input_data: Any) -> str:
        if isinstance(input_data, dict):
            if "input" in input_data:
                return str(input_data["input"])
            return json.dumps(input_data, ensure_ascii=False)

        return str(input_data)
