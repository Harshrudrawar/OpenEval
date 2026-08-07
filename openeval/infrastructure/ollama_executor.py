from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

from openeval.application.ports import TargetExecutor


@dataclass
class OllamaTargetExecutor(TargetExecutor):
    model: str
    base_url: str = "http://localhost:11434/api"

    def execute(self, case: Any) -> dict[str, Any]:
        input_data = getattr(case, "input_data", {})
        prompt = self._build_prompt(input_data)

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }

        request = urllib.request.Request(
            url=f"{self.base_url.rstrip('/')}/generate",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                response_data = json.loads(response.read().decode("utf-8"))
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Could not reach Ollama at {self.base_url}") from exc

        return {
            "output": {
                "response": response_data.get("response", ""),
            },
            "status": "ok",
            "model": self.model,
        }

    def _build_prompt(self, input_data: Any) -> str:
        if isinstance(input_data, dict):
            if "input" in input_data:
                return str(input_data["input"])
            return json.dumps(input_data, ensure_ascii=False)

        return str(input_data)
