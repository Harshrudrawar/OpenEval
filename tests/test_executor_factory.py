from __future__ import annotations

from openeval.infrastructure import (
    MockTargetExecutor,
    OllamaTargetExecutor,
    OpenAITargetExecutor,
)
from openeval.infrastructure.executor_factory import build_target_executor


def test_build_target_executor_returns_mock_for_unknown_provider() -> None:
    executor = build_target_executor({})

    assert isinstance(executor, MockTargetExecutor)


def test_build_target_executor_returns_ollama_executor() -> None:
    executor = build_target_executor({"provider": "ollama", "model": "llama3"})

    assert isinstance(executor, OllamaTargetExecutor)
    assert executor.model == "llama3"


def test_build_target_executor_returns_openai_executor(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "dummy-openai-key-for-tests")

    executor = build_target_executor({"provider": "openai", "model": "gpt-4o"})

    assert isinstance(executor, OpenAITargetExecutor)
    assert executor.model == "gpt-4o"
