from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any

from openeval.domain.plugins import MetricPlugin


def _normalize_structure(value: Any) -> Any:
    if isinstance(value, str):
        return value.strip().casefold()

    if isinstance(value, dict):
        return {
            str(key): _normalize_structure(inner_value)
            for key, inner_value in value.items()
        }

    if isinstance(value, list):
        return [_normalize_structure(item) for item in value]

    return value


def _flatten_text(value: Any) -> str:
    if isinstance(value, str):
        return value.strip().casefold()

    if isinstance(value, dict):
        parts = [_flatten_text(inner_value) for inner_value in value.values()]
        return " ".join(part for part in parts if part).strip()

    if isinstance(value, list):
        parts = [_flatten_text(item) for item in value]
        return " ".join(part for part in parts if part).strip()

    if value is None:
        return ""

    return str(value).strip().casefold()


def _contains_expected(
    expected_text: str,
    actual_text: str,
) -> bool:
    if not expected_text or not actual_text:
        return False

    pattern = rf"\b{re.escape(expected_text)}\b"
    return re.search(pattern, actual_text) is not None


def _read_non_negative_int(value: Any) -> int:
    if isinstance(value, bool):
        return 0

    if isinstance(value, int):
        return max(value, 0)

    return 0


@dataclass(frozen=True)
class OllamaGenerationResult:
    response_text: str
    input_tokens: int
    output_tokens: int
    total_tokens: int


def _ollama_generate(
    *,
    model: str,
    prompt: str,
    base_url: str,
) -> OllamaGenerationResult:
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
    }

    request = urllib.request.Request(
        url=f"{base_url.rstrip('/')}/generate",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=60,
        ) as response:
            response_data = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Could not reach Ollama at {base_url}") from exc

    input_tokens = _read_non_negative_int(response_data.get("prompt_eval_count"))

    output_tokens = _read_non_negative_int(response_data.get("eval_count"))

    return OllamaGenerationResult(
        response_text=str(response_data.get("response", "")),
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=input_tokens + output_tokens,
    )


def _build_judge_prompt(
    expected_output: dict[str, Any],
    actual_output: dict[str, Any],
) -> str:
    expected_json = json.dumps(
        expected_output,
        ensure_ascii=False,
        indent=2,
    )

    actual_json = json.dumps(
        actual_output,
        ensure_ascii=False,
        indent=2,
    )

    return f"""
You are a strict evaluation judge for LLM outputs.

Decide whether the actual output is correct with respect to the expected output.

Rules:

- Return only a JSON object.
- Use a score of 1.0 for correct and 0.0 for incorrect.
- Be conservative.
- Ignore style differences if the meaning is clearly correct.

Return this exact shape:
{{
  "verdict": "correct" or "incorrect",
  "score": 1.0 or 0.0,
  "reason": "short explanation"
}}

Expected output:
{expected_json}

Actual output:
{actual_json}
""".strip()


def _parse_judge_score(
    response_text: str,
) -> float:
    text = response_text.strip()

    if not text:
        raise ValueError("LLM judge returned an empty response")

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        parsed = None

    if isinstance(parsed, dict):
        score = parsed.get("score")

        if isinstance(score, (int, float)):
            return 1.0 if float(score) >= 0.5 else 0.0

        verdict = (
            str(
                parsed.get(
                    "verdict",
                    "",
                )
            )
            .strip()
            .casefold()
        )

        if verdict in {
            "correct",
            "yes",
            "true",
            "pass",
            "passed",
            "1",
        }:
            return 1.0

        if verdict in {
            "incorrect",
            "no",
            "false",
            "fail",
            "failed",
            "0",
        }:
            return 0.0

    lower_text = text.casefold()

    if re.search(
        r"\b(correct|yes|true|pass|passed)\b",
        lower_text,
    ):
        return 1.0

    if re.search(
        r"\b(incorrect|no|false|fail|failed)\b",
        lower_text,
    ):
        return 0.0

    raise ValueError("Could not parse LLM judge response: " f"{response_text}")


class AccuracyMetricPlugin(MetricPlugin):
    name = "accuracy"

    def evaluate(
        self,
        expected_output: dict[str, Any],
        actual_output: dict[str, Any],
    ) -> float:
        returned_output = actual_output.get(
            "output",
            {},
        )

        return (
            1.0
            if _normalize_structure(expected_output)
            == _normalize_structure(returned_output)
            else 0.0
        )


class ContainsMetricPlugin(MetricPlugin):
    name = "contains"

    def evaluate(
        self,
        expected_output: dict[str, Any],
        actual_output: dict[str, Any],
    ) -> float:
        returned_output = actual_output.get(
            "output",
            {},
        )

        expected_text = _flatten_text(expected_output)

        actual_text = _flatten_text(returned_output)

        return (
            1.0
            if _contains_expected(
                expected_text,
                actual_text,
            )
            else 0.0
        )


@dataclass
class OllamaJudgeMetricPlugin(MetricPlugin):
    name: str = "llm_judge"
    model: str = "llama3"
    base_url: str = "http://localhost:11434/api"

    _input_tokens: int = field(
        default=0,
        init=False,
        repr=False,
    )
    _output_tokens: int = field(
        default=0,
        init=False,
        repr=False,
    )
    _total_tokens: int = field(
        default=0,
        init=False,
        repr=False,
    )

    def evaluate(
        self,
        expected_output: dict[str, Any],
        actual_output: dict[str, Any],
    ) -> float:
        prompt = _build_judge_prompt(
            expected_output,
            actual_output,
        )

        result = _ollama_generate(
            model=self.model,
            prompt=prompt,
            base_url=self.base_url,
        )

        self._input_tokens += result.input_tokens
        self._output_tokens += result.output_tokens
        self._total_tokens += result.total_tokens

        return _parse_judge_score(result.response_text)

    def usage(self) -> dict[str, int]:
        return {
            "input_tokens": self._input_tokens,
            "output_tokens": self._output_tokens,
            "total_tokens": self._total_tokens,
        }


def build_metric_plugin(
    name: str,
    judge_config: dict[str, Any] | None = None,
) -> MetricPlugin:
    metric_name = name.strip().casefold()

    if metric_name == "accuracy":
        return AccuracyMetricPlugin()

    if metric_name == "contains":
        return ContainsMetricPlugin()

    if metric_name == "llm_judge":
        config = judge_config or {}

        provider = (
            str(
                config.get(
                    "provider",
                    "ollama",
                )
            )
            .strip()
            .casefold()
            or "ollama"
        )

        if provider != "ollama":
            raise ValueError(f"Unsupported judge provider: {provider}")

        model = (
            str(
                config.get(
                    "model",
                    "llama3",
                )
            ).strip()
            or "llama3"
        )

        base_url = (
            str(
                config.get(
                    "base_url",
                    "http://localhost:11434/api",
                )
            ).strip()
            or "http://localhost:11434/api"
        )

        return OllamaJudgeMetricPlugin(
            model=model,
            base_url=base_url,
        )

    raise ValueError(f"Unsupported metric plugin: {name}")
