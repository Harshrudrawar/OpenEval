from __future__ import annotations

from typing import Any

from openeval.application.ports import TargetExecutor
from openeval.infrastructure.ollama_executor import OllamaTargetExecutor
from openeval.infrastructure.openai_executor import OpenAITargetExecutor
from openeval.infrastructure.target_executors import MockTargetExecutor


def build_target_executor(target: dict[str, Any]) -> TargetExecutor:
    provider = str(target.get("provider", "mock")).strip().lower()

    if provider == "openai":
        model = str(target.get("model", "gpt-4o")).strip() or "gpt-4o"
        return OpenAITargetExecutor(model=model)

    if provider == "ollama":
        model = str(target.get("model", "llama3")).strip() or "llama3"
        base_url = (
            str(target.get("base_url", "http://localhost:11434/api")).strip()
            or "http://localhost:11434/api"
        )
        return OllamaTargetExecutor(model=model, base_url=base_url)

    return MockTargetExecutor()
