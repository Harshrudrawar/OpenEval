from __future__ import annotations

import argparse
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from openeval.application import (
    CreateEvaluationDefinitionUseCase,
    CreateRunUseCase,
    EvaluateCaseResultsUseCase,
    ExecuteCasesUseCase,
    LoadCasesFromDatasetUseCase,
)
from openeval.application.comparison_use_cases import CompareScoresUseCase
from openeval.domain.cases import CaseResult
from openeval.domain.plugins import MetricPlugin
from openeval.domain.scoring import Score
from openeval.infrastructure import (
    CsvDatasetLoader,
    InMemoryEvaluationRepository,
    InMemoryRunRepository,
)
from openeval.infrastructure.executor_factory import build_target_executor
from openeval.infrastructure.metric_plugins import build_metric_plugin
from openeval.interface.report import (
    TokenUsage,
    append_run_history,
    write_comparison_report,
    write_run_report,
)
from openeval.interface.yaml_loader import load_yaml

RUN_HISTORY_PATH = Path("reports") / "run-history.jsonl"


@dataclass(frozen=True)
class EvaluationInputs:
    name: str
    dataset_path: str
    dataset_version_id: str
    prompt_version_id: str
    metric_names: list[str]
    target: dict[str, Any]
    gate_config: dict[str, Any]
    judge_config: dict[str, Any]
    baseline: dict[str, Any] | None
    regression_config: dict[str, Any]


@dataclass(frozen=True)
class RunOutcome:
    evaluation_name: str
    evaluation_id: str
    run_id: str
    provider: str
    model: str
    metric_scores: dict[str, float]
    cases_count: int
    case_results_count: int
    accuracy: float
    latency_ms: float
    target_usage: TokenUsage
    judge_usage: TokenUsage
    combined_usage: TokenUsage
    gate_threshold: float | None
    gate_passed: bool | None
    report_path: Path | None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="openeval")
    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    create_parser = subparsers.add_parser(
        "create-evaluation",
        help="Create a new evaluation definition",
    )
    create_parser.add_argument("--name", required=True)
    create_parser.add_argument(
        "--dataset-version-id",
        required=True,
    )
    create_parser.add_argument(
        "--prompt-version-id",
        required=True,
    )
    create_parser.add_argument(
        "--target",
        required=True,
        help="Target model name",
    )
    create_parser.add_argument(
        "--metric-plugins",
        required=True,
        help="Comma-separated metric plugin names",
    )

    run_parser = subparsers.add_parser(
        "run",
        help="Run an evaluation from a YAML file",
    )
    run_parser.add_argument(
        "config_path",
        help="Path to evaluation YAML file",
    )

    compare_parser = subparsers.add_parser(
        "compare",
        help="Compare two providers on the same evaluation YAML",
    )
    compare_parser.add_argument(
        "config_path",
        help="Path to evaluation YAML file",
    )
    compare_parser.add_argument(
        "--left-provider",
        required=True,
        help="Left provider name",
    )
    compare_parser.add_argument(
        "--right-provider",
        required=True,
        help="Right provider name",
    )
    compare_parser.add_argument(
        "--left-model",
        default="",
        help="Left model name",
    )
    compare_parser.add_argument(
        "--right-model",
        default="",
        help="Right model name",
    )

    history_parser = subparsers.add_parser(
        "history",
        help="Show saved run and comparison history",
    )
    history_parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Number of history entries to show",
    )
    history_parser.add_argument(
        "--kind",
        choices=["all", "run", "comparison"],
        default="all",
        help="Filter history entries by kind",
    )

    return parser


def create_use_case() -> CreateEvaluationDefinitionUseCase:
    repository = InMemoryEvaluationRepository()
    return CreateEvaluationDefinitionUseCase(repository)


def print_evaluation_summary(evaluation: Any) -> None:
    print("✔ Evaluation created successfully")
    print()
    print(f"ID: {evaluation.id}")
    print(f"Name: {evaluation.name}")
    print(f"Dataset Version: {evaluation.dataset_version_id}")
    print(f"Prompt Version: {evaluation.prompt_version_id}")
    print(f"Metrics: {len(evaluation.metric_plugins)}")


def _default_model_for_provider(provider: str) -> str:
    provider_name = provider.strip().lower()

    if provider_name == "openai":
        return "gpt-4o"

    if provider_name == "ollama":
        return "llama3"

    return "unknown"


def _parse_metric_names_arg(raw_value: str) -> list[str]:
    metric_names = [part.strip() for part in raw_value.split(",")]
    metric_names = [metric_name for metric_name in metric_names if metric_name]

    if not metric_names:
        raise ValueError("metric-plugins must contain at least one metric name")

    if len(set(metric_names)) != len(metric_names):
        raise ValueError("metric-plugins must not contain duplicates")

    return metric_names


def _load_history_entries(
    history_path: Path = RUN_HISTORY_PATH,
) -> list[dict[str, Any]]:
    if not history_path.exists():
        return []

    entries: list[dict[str, Any]] = []

    for line in history_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()

        if not line:
            continue

        entries.append(json.loads(line))

    return entries


def _format_tri_state(value: Any) -> str:
    if value is True:
        return "PASSED"

    if value is False:
        return "FAILED"

    return "N/A"


def _history_text(
    entry: dict[str, Any],
    key: str,
) -> str | None:
    value = entry.get(key)

    if not isinstance(value, str):
        return None

    text = value.strip()
    return text or None


def _history_metric_names(
    entry: dict[str, Any],
) -> list[str]:
    raw_metric_names = entry.get("metric_names")

    if isinstance(raw_metric_names, list):
        metric_names = [
            str(metric_name).strip()
            for metric_name in raw_metric_names
            if str(metric_name).strip()
        ]

        if metric_names:
            return metric_names

    metric_name = _history_text(
        entry,
        "metric_name",
    )

    if metric_name is not None:
        parts = [part.strip() for part in metric_name.split(",")]
        metric_names = [part for part in parts if part]

        if metric_names:
            return metric_names

    return []


def _metric_signature(
    metric_names: list[str],
) -> str:
    return " | ".join(metric_names)


def _metric_key(
    metric_names: list[str],
) -> tuple[str, ...]:
    return tuple(sorted(metric_names))


def _read_non_negative_int(
    value: Any,
) -> int:
    if isinstance(value, bool):
        return 0

    if isinstance(value, int):
        return max(value, 0)

    return 0


def _usage_from_mapping(
    value: Any,
) -> TokenUsage:
    if not isinstance(value, dict):
        return TokenUsage()

    return TokenUsage(
        input_tokens=_read_non_negative_int(value.get("input_tokens", 0)),
        output_tokens=_read_non_negative_int(value.get("output_tokens", 0)),
        total_tokens=_read_non_negative_int(value.get("total_tokens", 0)),
    )


def _add_usage(
    left: TokenUsage,
    right: TokenUsage,
) -> TokenUsage:
    return TokenUsage(
        input_tokens=(left.input_tokens + right.input_tokens),
        output_tokens=(left.output_tokens + right.output_tokens),
        total_tokens=(left.total_tokens + right.total_tokens),
    )


def _aggregate_target_usage(
    case_results: list[CaseResult],
) -> TokenUsage:
    usage = TokenUsage()

    for case_result in case_results:
        case_usage = _usage_from_mapping(
            case_result.actual_output.get(
                "usage",
                {},
            )
        )
        usage = _add_usage(
            usage,
            case_usage,
        )

    return usage


def _aggregate_judge_usage(
    metric_plugins: list[MetricPlugin],
) -> TokenUsage:
    usage = TokenUsage()

    for plugin in metric_plugins:
        usage_method = getattr(
            plugin,
            "usage",
            None,
        )

        if not callable(usage_method):
            continue

        plugin_usage = usage_method()

        usage = _add_usage(
            usage,
            _usage_from_mapping(plugin_usage),
        )

    return usage


def history_from_jsonl(
    limit: int = 20,
    kind: str = "all",
) -> int:
    if limit <= 0:
        raise ValueError("history limit must be greater than 0")

    entries = _load_history_entries()

    if kind != "all":
        entries = [
            entry
            for entry in entries
            if entry.get(
                "kind",
                "unknown",
            )
            == kind
        ]

    if not entries:
        if kind == "all":
            print("No history yet.")
        else:
            print(f"No {kind} history yet.")

        return 0

    print("OpenEval History")
    print()

    for entry in reversed(entries[-limit:]):
        entry_kind = entry.get(
            "kind",
            "unknown",
        )

        if entry_kind == "run":
            gate_status = _format_tri_state(entry.get("gate_passed"))
            regression_status = _format_tri_state(entry.get("regression_passed"))

            metric_names = _history_metric_names(entry)
            metric_display = _metric_signature(metric_names) if metric_names else ""

            print("RUN")
            print(f"Evaluation: " f"{entry.get('evaluation_name', '')}")
            print(f"Provider: " f"{entry.get('provider', '')}")
            print(f"Model: " f"{entry.get('model', '')}")
            print(f"Metrics: " f"{metric_display}")

            judge_provider = _history_text(
                entry,
                "judge_provider",
            )
            judge_model = _history_text(
                entry,
                "judge_model",
            )

            if judge_provider is not None or judge_model is not None:
                print(
                    f"Judge: "
                    f"{judge_provider or 'unknown'}:"
                    f"{judge_model or 'unknown'}"
                )

            print(f"Accuracy: " f"{float(entry.get('accuracy', 0.0)):.2f}")

            print()
            print("Usage")

            print("Target")
            print(f"  Input Tokens: " f"{int(entry.get('input_tokens', 0)):,}")
            print(f"  Output Tokens: " f"{int(entry.get('output_tokens', 0)):,}")
            print(f"  Total Tokens: " f"{int(entry.get('total_tokens', 0)):,}")

            print("Judge")
            print(f"  Input Tokens: " f"{int(entry.get('judge_input_tokens', 0)):,}")
            print(f"  Output Tokens: " f"{int(entry.get('judge_output_tokens', 0)):,}")
            print(f"  Total Tokens: " f"{int(entry.get('judge_total_tokens', 0)):,}")

            print("Combined")
            print(f"  Input Tokens: " f"{int(entry.get('combined_input_tokens', 0)):,}")
            print(
                f"  Output Tokens: " f"{int(entry.get('combined_output_tokens', 0)):,}"
            )
            print(f"  Total Tokens: " f"{int(entry.get('combined_total_tokens', 0)):,}")

            print()
            print(f"Gate: {gate_status}")
            print(f"Regression: " f"{regression_status}")

            baseline_source = entry.get("baseline_source")

            if baseline_source is not None:
                print(f"Baseline Source: " f"{baseline_source}")

            if "baseline_found" in entry:
                baseline_found = "yes" if entry.get("baseline_found") else "no"
                print(f"Baseline Found: " f"{baseline_found}")

            print()
            continue

        if entry_kind == "comparison":
            print("COMPARISON")
            print(f"Left: " f"{entry.get('left_name', '')}")
            print(f"Right: " f"{entry.get('right_name', '')}")
            print(f"Winner: " f"{entry.get('winner', '')}")
            print(f"Margin: " f"{float(entry.get('margin', 0.0)):.2f}")
            print()

            continue

        print("UNKNOWN")
        print(entry)
        print()

    return 0


def _load_inputs(
    config_path: str,
) -> EvaluationInputs:
    config = load_yaml(config_path)

    name = config.get("name", "")
    dataset_config = config.get(
        "dataset",
        {},
    )
    prompt_config = config.get(
        "prompt",
        {},
    )
    target = config.get(
        "target",
        {},
    )
    metrics = config.get(
        "metrics",
        [],
    )
    gate_config = config.get(
        "gate",
        {},
    )
    judge_config = config.get(
        "judge",
        {},
    )
    baseline = config.get("baseline")
    regression_config = config.get(
        "regression",
        {},
    )

    if not isinstance(
        dataset_config,
        dict,
    ):
        raise ValueError("dataset must be a YAML mapping/object")

    if not isinstance(
        prompt_config,
        dict,
    ):
        raise ValueError("prompt must be a YAML mapping/object")

    if not isinstance(
        target,
        dict,
    ):
        raise ValueError("target must be a YAML mapping/object")

    if not isinstance(
        metrics,
        list,
    ):
        raise ValueError("metrics must be a YAML list")

    if gate_config is None:
        gate_config = {}

    if not isinstance(
        gate_config,
        dict,
    ):
        raise ValueError("gate must be a YAML mapping/object")

    if judge_config is None:
        judge_config = {}

    if not isinstance(
        judge_config,
        dict,
    ):
        raise ValueError("judge must be a YAML mapping/object")

    if baseline is not None and not isinstance(
        baseline,
        dict,
    ):
        raise ValueError("baseline must be a YAML mapping/object")

    if regression_config is None:
        regression_config = {}

    if not isinstance(
        regression_config,
        dict,
    ):
        raise ValueError("regression must be a YAML mapping/object")

    dataset_path = dataset_config.get(
        "path",
        "",
    )

    if (
        not isinstance(
            dataset_path,
            str,
        )
        or not dataset_path.strip()
    ):
        raise ValueError("dataset.path must be a non-empty string")

    dataset_version_id = dataset_config.get(
        "version",
        "",
    )

    if (
        not isinstance(
            dataset_version_id,
            str,
        )
        or not dataset_version_id.strip()
    ):
        raise ValueError("dataset.version must be a non-empty string")

    prompt_version_id = prompt_config.get(
        "version",
        "",
    )

    if (
        not isinstance(
            prompt_version_id,
            str,
        )
        or not prompt_version_id.strip()
    ):
        raise ValueError("prompt.version must be a non-empty string")

    if not metrics:
        raise ValueError("metrics must contain at least one metric")

    metric_names: list[str] = []

    for metric_name in metrics:
        if (
            not isinstance(
                metric_name,
                str,
            )
            or not metric_name.strip()
        ):
            raise ValueError("each metrics entry must be a non-empty string")

        metric_names.append(metric_name.strip())

    if len(set(metric_names)) != len(metric_names):
        raise ValueError("metrics must not contain duplicates")

    return EvaluationInputs(
        name=name,
        dataset_path=dataset_path,
        dataset_version_id=dataset_version_id,
        prompt_version_id=prompt_version_id,
        metric_names=metric_names,
        target=target,
        gate_config=gate_config,
        judge_config=judge_config,
        baseline=baseline,
        regression_config=regression_config,
    )


def _resolve_target(
    base_target: dict[str, Any],
    *,
    provider: str,
    model: str,
) -> dict[str, Any]:
    resolved_target = dict(base_target)

    provider_name = provider.strip().lower()
    resolved_target["provider"] = provider_name

    model_name = model.strip()

    if not model_name:
        model_name = _default_model_for_provider(provider_name)

    resolved_target["model"] = model_name

    return resolved_target


def _judge_details(
    inputs: EvaluationInputs,
) -> tuple[str | None, str | None]:
    if "llm_judge" not in inputs.metric_names:
        return None, None

    judge_provider = (
        str(
            inputs.judge_config.get(
                "provider",
                "ollama",
            )
        ).strip()
        or "ollama"
    )

    judge_model = (
        str(
            inputs.judge_config.get(
                "model",
                "llama3",
            )
        ).strip()
        or "llama3"
    )

    return (
        judge_provider,
        judge_model,
    )


def _metric_plugins_for_inputs(
    inputs: EvaluationInputs,
) -> list[MetricPlugin]:
    plugins: list[MetricPlugin] = []

    for metric_name in inputs.metric_names:
        if metric_name == "llm_judge":
            plugins.append(
                build_metric_plugin(
                    metric_name,
                    inputs.judge_config,
                )
            )
        else:
            plugins.append(build_metric_plugin(metric_name))

    return plugins


def _score_by_metric(
    scores: list[Score],
    metric_names: list[str],
) -> dict[str, float]:
    totals: dict[str, float] = {metric_name: 0.0 for metric_name in metric_names}

    counts: dict[str, int] = {metric_name: 0 for metric_name in metric_names}

    for score in scores:
        if score.name not in totals:
            totals[score.name] = 0.0
            counts[score.name] = 0

        totals[score.name] += score.value
        counts[score.name] += 1

    metric_scores: dict[str, float] = {}

    for metric_name in metric_names:
        count = counts.get(
            metric_name,
            0,
        )

        metric_scores[metric_name] = (
            totals.get(
                metric_name,
                0.0,
            )
            / count
            if count
            else 0.0
        )

    return metric_scores


def _find_historical_baseline(
    inputs: EvaluationInputs,
    *,
    provider: str,
    model: str,
) -> RunOutcome | None:
    entries = _load_history_entries()
    expected_metric_key = _metric_key(inputs.metric_names)

    for entry in reversed(entries):
        if entry.get("kind") != "run":
            continue

        entry_metric_key = _metric_key(_history_metric_names(entry))

        for key, expected in (
            (
                "evaluation_name",
                inputs.name,
            ),
            (
                "dataset_version_id",
                inputs.dataset_version_id,
            ),
            (
                "prompt_version_id",
                inputs.prompt_version_id,
            ),
            (
                "provider",
                provider,
            ),
            (
                "model",
                model,
            ),
        ):
            if (
                _history_text(
                    entry,
                    key,
                )
                != expected
            ):
                break
        else:
            if entry_metric_key != expected_metric_key:
                continue

            if entry.get("gate_passed") is False:
                continue

            if entry.get("regression_passed") is False:
                continue

            run_id = _history_text(
                entry,
                "run_id",
            )
            evaluation_id = _history_text(
                entry,
                "evaluation_id",
            )
            evaluation_name = _history_text(
                entry,
                "evaluation_name",
            )
            entry_provider = _history_text(
                entry,
                "provider",
            )
            entry_model = _history_text(
                entry,
                "model",
            )

            if (
                run_id is None
                or evaluation_id is None
                or evaluation_name is None
                or entry_provider is None
                or entry_model is None
            ):
                continue

            try:
                accuracy = float(
                    entry.get(
                        "accuracy",
                        0.0,
                    )
                )
            except (
                TypeError,
                ValueError,
            ):
                continue

            try:
                latency_ms = float(
                    entry.get(
                        "latency_ms",
                        0.0,
                    )
                )
            except (
                TypeError,
                ValueError,
            ):
                latency_ms = 0.0

            gate_passed_raw = entry.get("gate_passed")

            gate_passed = (
                gate_passed_raw
                if isinstance(
                    gate_passed_raw,
                    bool,
                )
                else None
            )

            metric_scores_raw = entry.get("metric_scores")

            metric_scores: dict[
                str,
                float,
            ] = {}

            if isinstance(
                metric_scores_raw,
                dict,
            ):
                for key, value in metric_scores_raw.items():
                    if isinstance(
                        key,
                        str,
                    ) and isinstance(
                        value,
                        (int, float),
                    ):
                        metric_scores[key] = float(value)

            target_usage = TokenUsage(
                input_tokens=(
                    _read_non_negative_int(
                        entry.get(
                            "input_tokens",
                            0,
                        )
                    )
                ),
                output_tokens=(
                    _read_non_negative_int(
                        entry.get(
                            "output_tokens",
                            0,
                        )
                    )
                ),
                total_tokens=(
                    _read_non_negative_int(
                        entry.get(
                            "total_tokens",
                            0,
                        )
                    )
                ),
            )

            judge_usage = TokenUsage(
                input_tokens=(
                    _read_non_negative_int(
                        entry.get(
                            "judge_input_tokens",
                            0,
                        )
                    )
                ),
                output_tokens=(
                    _read_non_negative_int(
                        entry.get(
                            "judge_output_tokens",
                            0,
                        )
                    )
                ),
                total_tokens=(
                    _read_non_negative_int(
                        entry.get(
                            "judge_total_tokens",
                            0,
                        )
                    )
                ),
            )

            combined_usage = TokenUsage(
                input_tokens=(
                    _read_non_negative_int(
                        entry.get(
                            "combined_input_tokens",
                            target_usage.input_tokens + judge_usage.input_tokens,
                        )
                    )
                ),
                output_tokens=(
                    _read_non_negative_int(
                        entry.get(
                            "combined_output_tokens",
                            target_usage.output_tokens + judge_usage.output_tokens,
                        )
                    )
                ),
                total_tokens=(
                    _read_non_negative_int(
                        entry.get(
                            "combined_total_tokens",
                            target_usage.total_tokens + judge_usage.total_tokens,
                        )
                    )
                ),
            )

            return RunOutcome(
                evaluation_name=evaluation_name,
                evaluation_id=evaluation_id,
                run_id=run_id,
                provider=entry_provider,
                model=entry_model,
                metric_scores=metric_scores,
                cases_count=0,
                case_results_count=0,
                accuracy=accuracy,
                latency_ms=latency_ms,
                target_usage=target_usage,
                judge_usage=judge_usage,
                combined_usage=combined_usage,
                gate_threshold=None,
                gate_passed=gate_passed,
                report_path=None,
            )

    return None


def _execute_single_run(
    inputs: EvaluationInputs,
    *,
    target: dict[str, Any],
    write_report: bool,
) -> RunOutcome:
    started_at = time.perf_counter()

    evaluation_use_case = create_use_case()

    evaluation = evaluation_use_case.execute(
        name=inputs.name,
        dataset_version_id=inputs.dataset_version_id,
        prompt_version_id=inputs.prompt_version_id,
        target=target,
        metric_plugins=[{"name": metric_name} for metric_name in inputs.metric_names],
        gate=inputs.gate_config or None,
    )

    dataset_loader = CsvDatasetLoader()
    load_cases_use_case = LoadCasesFromDatasetUseCase(dataset_loader)

    cases = load_cases_use_case.execute(
        dataset_path=inputs.dataset_path,
        evaluation_definition_id=evaluation.id,
    )

    run_repository = InMemoryRunRepository()
    run_use_case = CreateRunUseCase(run_repository)
    run = run_use_case.execute(evaluation.id)

    target_executor = build_target_executor(target)

    execute_cases_use_case = ExecuteCasesUseCase(target_executor)

    case_results = execute_cases_use_case.execute(
        cases,
        run.id,
    )

    target_usage = _aggregate_target_usage(case_results)

    metric_plugins = _metric_plugins_for_inputs(inputs)

    score_use_case = EvaluateCaseResultsUseCase(metric_plugins)

    scores = score_use_case.execute(
        case_results,
        case_results,
    )

    metric_scores = _score_by_metric(
        scores,
        inputs.metric_names,
    )

    judge_usage = _aggregate_judge_usage(metric_plugins)

    combined_usage = _add_usage(
        target_usage,
        judge_usage,
    )

    overall_score = (
        sum(metric_scores.values()) / len(metric_scores) if metric_scores else 0.0
    )

    latency_ms = (time.perf_counter() - started_at) * 1000

    gate_threshold_raw = inputs.gate_config.get("accuracy")

    gate_threshold: float | None = None
    gate_passed: bool | None = None

    if gate_threshold_raw is not None:
        try:
            gate_threshold = float(gate_threshold_raw)
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError("gate.accuracy must be a number") from exc

        gate_passed = overall_score >= gate_threshold

    provider = (
        str(
            target.get(
                "provider",
                "mock",
            )
        ).strip()
        or "mock"
    )

    model = (
        str(
            target.get(
                "model",
                "unknown",
            )
        ).strip()
        or "unknown"
    )

    judge_provider, judge_model = _judge_details(inputs)

    report_path: Path | None = None

    if write_report:
        report_path = write_run_report(
            "reports",
            evaluation_name=evaluation.name,
            evaluation_id=evaluation.id,
            run_id=run.id,
            dataset_version=(inputs.dataset_version_id),
            prompt_version=(inputs.prompt_version_id),
            provider=provider,
            model=model,
            metric_scores=metric_scores,
            judge_provider=judge_provider,
            judge_model=judge_model,
            cases_count=len(cases),
            case_results_count=len(case_results),
            overall_score=overall_score,
            latency_ms=latency_ms,
            target_usage=target_usage,
            judge_usage=judge_usage,
            combined_usage=combined_usage,
            gate_threshold=gate_threshold,
            gate_passed=gate_passed,
        )

    return RunOutcome(
        evaluation_name=evaluation.name,
        evaluation_id=evaluation.id,
        run_id=run.id,
        provider=provider,
        model=model,
        metric_scores=metric_scores,
        cases_count=len(cases),
        case_results_count=len(case_results),
        accuracy=overall_score,
        latency_ms=latency_ms,
        target_usage=target_usage,
        judge_usage=judge_usage,
        combined_usage=combined_usage,
        gate_threshold=gate_threshold,
        gate_passed=gate_passed,
        report_path=report_path,
    )


def _print_regression_summary(
    *,
    current: RunOutcome,
    baseline: RunOutcome,
    header: str = "Baseline Regression Check",
) -> None:
    delta = current.accuracy - baseline.accuracy

    if delta > 0:
        status = "IMPROVED"
    elif delta < 0:
        status = "REGRESSED"
    else:
        status = "UNCHANGED"

    print()
    print(header)

    print(
        f"Baseline "
        f"({baseline.provider}:{baseline.model}): "
        f"{baseline.accuracy:.2f}"
    )

    print(
        f"Current  " f"({current.provider}:{current.model}): " f"{current.accuracy:.2f}"
    )

    print(f"Delta: {delta:+.2f}")
    print(f"Result: {status}")


def run_from_yaml(
    config_path: str,
) -> int:
    inputs = _load_inputs(config_path)

    outcome = _execute_single_run(
        inputs,
        target=inputs.target,
        write_report=True,
    )

    print_evaluation_summary(
        type(
            "EvaluationSummary",
            (),
            {
                "id": outcome.evaluation_id,
                "name": outcome.evaluation_name,
                "dataset_version_id": (inputs.dataset_version_id),
                "prompt_version_id": (inputs.prompt_version_id),
                "metric_plugins": [
                    {"name": metric_name} for metric_name in inputs.metric_names
                ],
            },
        )()
    )

    print()
    print(f"Loaded {outcome.cases_count} cases")
    print(f"Created {outcome.case_results_count} " f"case results")

    print(f"Overall Score: " f"{outcome.accuracy:.2f}")

    print("Metric Scores:")

    for metric_name in inputs.metric_names:
        print(f"  {metric_name}: " f"{outcome.metric_scores.get(metric_name, 0.0):.2f}")

    print()
    print("Usage")

    print("Target")
    print(f"  Input Tokens: " f"{outcome.target_usage.input_tokens:,}")
    print(f"  Output Tokens: " f"{outcome.target_usage.output_tokens:,}")
    print(f"  Total Tokens: " f"{outcome.target_usage.total_tokens:,}")

    print("Judge")
    print(f"  Input Tokens: " f"{outcome.judge_usage.input_tokens:,}")
    print(f"  Output Tokens: " f"{outcome.judge_usage.output_tokens:,}")
    print(f"  Total Tokens: " f"{outcome.judge_usage.total_tokens:,}")

    print("Combined")
    print(f"  Input Tokens: " f"{outcome.combined_usage.input_tokens:,}")
    print(f"  Output Tokens: " f"{outcome.combined_usage.output_tokens:,}")
    print(f"  Total Tokens: " f"{outcome.combined_usage.total_tokens:,}")

    print()
    print(f"Latency: " f"{outcome.latency_ms:.0f} ms")

    if outcome.gate_threshold is None:
        print("Quality Gate: Not configured")
        exit_code = 0
    else:
        gate_status = "PASSED" if outcome.gate_passed else "FAILED"

        print(
            f"Quality Gate: {gate_status} "
            f"(threshold: "
            f"{outcome.gate_threshold:.2f})"
        )

        exit_code = 0 if outcome.gate_passed else 1

    baseline_source: str | None = None
    baseline_provider: str | None = None
    baseline_model: str | None = None
    baseline_run_id: str | None = None
    baseline_outcome: RunOutcome | None = None
    regression_delta: float | None = None
    regression_passed: bool | None = None
    baseline_found: bool | None = None

    if inputs.baseline is not None:
        baseline_source = (
            str(
                inputs.baseline.get(
                    "source",
                    "explicit",
                )
            )
            .strip()
            .lower()
            or "explicit"
        )

        if baseline_source == "history":
            baseline_outcome = _find_historical_baseline(
                inputs,
                provider=outcome.provider,
                model=outcome.model,
            )

            baseline_found = baseline_outcome is not None

            if baseline_outcome is None:
                print()
                print("Historical Baseline Check")
                print("No matching historical " "baseline found.")
                print("Regression Gate: FAILED")
                exit_code = 1
            else:
                baseline_provider = baseline_outcome.provider
                baseline_model = baseline_outcome.model
                baseline_run_id = baseline_outcome.run_id

                regression_raw = inputs.regression_config.get(
                    "max_drop",
                    0.0,
                )

                try:
                    max_drop = float(regression_raw)
                except (
                    TypeError,
                    ValueError,
                ) as exc:
                    raise ValueError("regression.max_drop " "must be a number") from exc

                if max_drop < 0:
                    raise ValueError(
                        "regression.max_drop " "must be greater than or " "equal to 0"
                    )

                regression_delta = outcome.accuracy - baseline_outcome.accuracy

                regression_passed = regression_delta >= -max_drop

                _print_regression_summary(
                    current=outcome,
                    baseline=baseline_outcome,
                    header=("Historical Baseline Check"),
                )

                print(f"Allowed Drop: " f"{max_drop:.2f}")

                print(
                    "Regression Gate: " f"{'PASSED' if regression_passed else 'FAILED'}"
                )

                if not regression_passed:
                    exit_code = 1

        else:
            baseline_provider = (
                str(
                    inputs.baseline.get(
                        "provider",
                        "mock",
                    )
                ).strip()
                or "mock"
            )

            baseline_model = str(
                inputs.baseline.get(
                    "model",
                    "",
                )
            ).strip()

            baseline_target = _resolve_target(
                inputs.target,
                provider=baseline_provider,
                model=baseline_model,
            )

            baseline_outcome = _execute_single_run(
                inputs,
                target=baseline_target,
                write_report=False,
            )

            baseline_found = True
            baseline_provider = baseline_outcome.provider
            baseline_model = baseline_outcome.model
            baseline_run_id = baseline_outcome.run_id

            regression_raw = inputs.regression_config.get(
                "max_drop",
                0.0,
            )

            try:
                max_drop = float(regression_raw)
            except (
                TypeError,
                ValueError,
            ) as exc:
                raise ValueError("regression.max_drop " "must be a number") from exc

            if max_drop < 0:
                raise ValueError(
                    "regression.max_drop " "must be greater than or " "equal to 0"
                )

            regression_delta = outcome.accuracy - baseline_outcome.accuracy

            regression_passed = regression_delta >= -max_drop

            _print_regression_summary(
                current=outcome,
                baseline=baseline_outcome,
            )

            print(f"Allowed Drop: " f"{max_drop:.2f}")

            print("Regression Gate: " f"{'PASSED' if regression_passed else 'FAILED'}")

            if not regression_passed:
                exit_code = 1

    judge_provider, judge_model = _judge_details(inputs)

    metric_names_text = _metric_signature(inputs.metric_names)

    history_path = append_run_history(
        {
            "kind": "run",
            "timestamp": time.time(),
            "evaluation_name": (outcome.evaluation_name),
            "evaluation_id": (outcome.evaluation_id),
            "run_id": outcome.run_id,
            "dataset_version_id": (inputs.dataset_version_id),
            "prompt_version_id": (inputs.prompt_version_id),
            "metric_name": metric_names_text,
            "metric_names": inputs.metric_names,
            "metric_scores": (outcome.metric_scores),
            "judge_provider": judge_provider,
            "judge_model": judge_model,
            "provider": outcome.provider,
            "model": outcome.model,
            # Backward-compatible target usage.
            "input_tokens": (outcome.target_usage.input_tokens),
            "output_tokens": (outcome.target_usage.output_tokens),
            "total_tokens": (outcome.target_usage.total_tokens),
            # Explicit judge usage.
            "judge_input_tokens": (outcome.judge_usage.input_tokens),
            "judge_output_tokens": (outcome.judge_usage.output_tokens),
            "judge_total_tokens": (outcome.judge_usage.total_tokens),
            # Combined usage.
            "combined_input_tokens": (outcome.combined_usage.input_tokens),
            "combined_output_tokens": (outcome.combined_usage.output_tokens),
            "combined_total_tokens": (outcome.combined_usage.total_tokens),
            "accuracy": outcome.accuracy,
            "latency_ms": (outcome.latency_ms),
            "gate_threshold": (outcome.gate_threshold),
            "gate_passed": (outcome.gate_passed),
            "baseline_source": (baseline_source),
            "baseline_found": (baseline_found),
            "baseline_run_id": (baseline_run_id),
            "baseline_provider": (baseline_provider),
            "baseline_model": (baseline_model),
            "baseline_accuracy": (
                baseline_outcome.accuracy if baseline_outcome is not None else None
            ),
            "regression_delta": (regression_delta),
            "regression_passed": (regression_passed),
        }
    )

    print()
    print("Run created successfully")
    print(f"Run ID: {outcome.run_id}")
    print("Run Status: created")

    print()

    if outcome.report_path is not None:
        print(f"Report written to: " f"{outcome.report_path}")

    print(f"History written to: " f"{history_path}")

    return exit_code


def compare_from_yaml(
    config_path: str,
    *,
    left_provider: str,
    right_provider: str,
    left_model: str,
    right_model: str,
) -> int:
    inputs = _load_inputs(config_path)

    left_target = _resolve_target(
        inputs.target,
        provider=left_provider,
        model=left_model,
    )

    right_target = _resolve_target(
        inputs.target,
        provider=right_provider,
        model=right_model,
    )

    left_outcome = _execute_single_run(
        inputs,
        target=left_target,
        write_report=False,
    )

    right_outcome = _execute_single_run(
        inputs,
        target=right_target,
        write_report=False,
    )

    comparison = CompareScoresUseCase().execute(
        left_name=(f"{left_outcome.provider}:" f"{left_outcome.model}"),
        right_name=(f"{right_outcome.provider}:" f"{right_outcome.model}"),
        left_accuracy=(left_outcome.accuracy),
        right_accuracy=(right_outcome.accuracy),
    )

    print("✔ Comparison completed successfully")
    print()

    print(f"Dataset Version: " f"{inputs.dataset_version_id}")
    print(f"Prompt Version: " f"{inputs.prompt_version_id}")

    print()

    print(f"Left  ({comparison.left_name}): " f"{comparison.left_accuracy:.2f}")

    print(f"Right ({comparison.right_name}): " f"{comparison.right_accuracy:.2f}")

    print(f"Winner: " f"{comparison.winner}")

    print(f"Margin: " f"{comparison.margin:.2f}")

    report_path = write_comparison_report(
        "reports",
        evaluation_name=inputs.name,
        evaluation_id=(left_outcome.evaluation_id),
        dataset_version=(inputs.dataset_version_id),
        prompt_version=(inputs.prompt_version_id),
        left_name=(f"{left_outcome.provider}:" f"{left_outcome.model}"),
        right_name=(f"{right_outcome.provider}:" f"{right_outcome.model}"),
        left_accuracy=(left_outcome.accuracy),
        right_accuracy=(right_outcome.accuracy),
        winner=comparison.winner,
        margin=comparison.margin,
    )

    print()
    print(f"Report written to: " f"{report_path}")

    history_path = append_run_history(
        {
            "kind": "comparison",
            "timestamp": time.time(),
            "evaluation_name": inputs.name,
            "evaluation_id": (left_outcome.evaluation_id),
            "dataset_version_id": (inputs.dataset_version_id),
            "prompt_version_id": (inputs.prompt_version_id),
            "metric_names": (inputs.metric_names),
            "left_name": (f"{left_outcome.provider}:" f"{left_outcome.model}"),
            "right_name": (f"{right_outcome.provider}:" f"{right_outcome.model}"),
            "left_accuracy": (left_outcome.accuracy),
            "right_accuracy": (right_outcome.accuracy),
            "winner": comparison.winner,
            "margin": comparison.margin,
            "left_target_input_tokens": (left_outcome.target_usage.input_tokens),
            "left_target_output_tokens": (left_outcome.target_usage.output_tokens),
            "left_target_total_tokens": (left_outcome.target_usage.total_tokens),
            "left_judge_input_tokens": (left_outcome.judge_usage.input_tokens),
            "left_judge_output_tokens": (left_outcome.judge_usage.output_tokens),
            "left_judge_total_tokens": (left_outcome.judge_usage.total_tokens),
            "left_combined_total_tokens": (left_outcome.combined_usage.total_tokens),
            "right_target_input_tokens": (right_outcome.target_usage.input_tokens),
            "right_target_output_tokens": (right_outcome.target_usage.output_tokens),
            "right_target_total_tokens": (right_outcome.target_usage.total_tokens),
            "right_judge_input_tokens": (right_outcome.judge_usage.input_tokens),
            "right_judge_output_tokens": (right_outcome.judge_usage.output_tokens),
            "right_judge_total_tokens": (right_outcome.judge_usage.total_tokens),
            "right_combined_total_tokens": (right_outcome.combined_usage.total_tokens),
        }
    )

    print(f"History written to: " f"{history_path}")

    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "create-evaluation":
        use_case = create_use_case()

        metric_names = _parse_metric_names_arg(args.metric_plugins)

        evaluation = use_case.execute(
            name=args.name,
            dataset_version_id=(args.dataset_version_id),
            prompt_version_id=(args.prompt_version_id),
            target={"provider": args.target},
            metric_plugins=[{"name": metric_name} for metric_name in metric_names],
        )

        print_evaluation_summary(evaluation)

        return 0

    if args.command == "run":
        return run_from_yaml(args.config_path)

    if args.command == "compare":
        return compare_from_yaml(
            args.config_path,
            left_provider=args.left_provider,
            right_provider=args.right_provider,
            left_model=args.left_model,
            right_model=args.right_model,
        )

    if args.command == "history":
        return history_from_jsonl(
            args.limit,
            args.kind,
        )

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
