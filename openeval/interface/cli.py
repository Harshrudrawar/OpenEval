from __future__ import annotations

import argparse
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
from openeval.infrastructure import (
    CsvDatasetLoader,
    InMemoryEvaluationRepository,
    InMemoryRunRepository,
)
from openeval.infrastructure.executor_factory import build_target_executor
from openeval.infrastructure.metric_plugins import build_metric_plugin
from openeval.interface.report import write_comparison_report, write_run_report
from openeval.interface.yaml_loader import load_yaml


@dataclass(frozen=True)
class EvaluationInputs:
    name: str
    dataset_path: str
    dataset_version_id: str
    prompt_version_id: str
    metric_name: str
    target: dict[str, Any]
    gate_config: dict[str, Any]
    baseline: dict[str, Any] | None
    regression_config: dict[str, Any]


@dataclass(frozen=True)
class RunOutcome:
    evaluation_name: str
    evaluation_id: str
    run_id: str
    provider: str
    model: str
    cases_count: int
    case_results_count: int
    accuracy: float
    latency_ms: float
    gate_threshold: float | None
    gate_passed: bool | None
    report_path: Path | None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="openeval")
    subparsers = parser.add_subparsers(dest="command", required=True)

    create_parser = subparsers.add_parser(
        "create-evaluation",
        help="Create a new evaluation definition",
    )
    create_parser.add_argument("--name", required=True)
    create_parser.add_argument("--dataset-version-id", required=True)
    create_parser.add_argument("--prompt-version-id", required=True)
    create_parser.add_argument(
        "--target",
        required=True,
        help="Target model name",
    )
    create_parser.add_argument(
        "--metric-plugins",
        required=True,
        help="Metric plugin name",
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


def _load_inputs(config_path: str) -> EvaluationInputs:
    config = load_yaml(config_path)

    name = config.get("name", "")
    dataset_config = config.get("dataset", {})
    prompt_config = config.get("prompt", {})
    target = config.get("target", {})
    metrics = config.get("metrics", [])
    gate_config = config.get("gate", {})
    baseline = config.get("baseline")
    regression_config = config.get("regression", {})

    if not isinstance(dataset_config, dict):
        raise ValueError("dataset must be a YAML mapping/object")

    if not isinstance(prompt_config, dict):
        raise ValueError("prompt must be a YAML mapping/object")

    if not isinstance(target, dict):
        raise ValueError("target must be a YAML mapping/object")

    if not isinstance(metrics, list):
        raise ValueError("metrics must be a YAML list")

    if gate_config is None:
        gate_config = {}

    if not isinstance(gate_config, dict):
        raise ValueError("gate must be a YAML mapping/object")

    if baseline is not None and not isinstance(baseline, dict):
        raise ValueError("baseline must be a YAML mapping/object")

    if regression_config is None:
        regression_config = {}

    if not isinstance(regression_config, dict):
        raise ValueError("regression must be a YAML mapping/object")

    dataset_path = dataset_config.get("path", "")
    if not isinstance(dataset_path, str) or not dataset_path.strip():
        raise ValueError("dataset.path must be a non-empty string")

    dataset_version_id = dataset_config.get("version", "")
    if not isinstance(dataset_version_id, str) or not dataset_version_id.strip():
        raise ValueError("dataset.version must be a non-empty string")

    prompt_version_id = prompt_config.get("version", "")
    if not isinstance(prompt_version_id, str) or not prompt_version_id.strip():
        raise ValueError("prompt.version must be a non-empty string")

    if len(metrics) != 1:
        raise ValueError("metrics must contain exactly one metric for now")

    metric_name = metrics[0]
    if not isinstance(metric_name, str) or not metric_name.strip():
        raise ValueError("metrics[0] must be a non-empty string")

    return EvaluationInputs(
        name=name,
        dataset_path=dataset_path,
        dataset_version_id=dataset_version_id,
        prompt_version_id=prompt_version_id,
        metric_name=metric_name.strip(),
        target=target,
        gate_config=gate_config,
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
        metric_plugins=[{"name": inputs.metric_name}],
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
    case_results = execute_cases_use_case.execute(cases, run.id)

    metric_plugin = build_metric_plugin(inputs.metric_name)
    score_use_case = EvaluateCaseResultsUseCase(metric_plugin)
    scores = score_use_case.execute(case_results, case_results)

    accuracy = sum(score.value for score in scores) / len(scores) if scores else 0.0
    latency_ms = (time.perf_counter() - started_at) * 1000

    gate_threshold_raw = inputs.gate_config.get("accuracy")
    gate_threshold: float | None = None
    gate_passed: bool | None = None

    if gate_threshold_raw is not None:
        try:
            gate_threshold = float(gate_threshold_raw)
        except (TypeError, ValueError) as exc:
            raise ValueError("gate.accuracy must be a number") from exc

        gate_passed = accuracy >= gate_threshold

    provider = str(target.get("provider", "mock")).strip() or "mock"
    model = str(target.get("model", "unknown")).strip() or "unknown"

    report_path: Path | None = None

    if write_report:
        report_path = write_run_report(
            "reports",
            evaluation_name=evaluation.name,
            evaluation_id=evaluation.id,
            run_id=run.id,
            dataset_version=inputs.dataset_version_id,
            prompt_version=inputs.prompt_version_id,
            provider=provider,
            model=model,
            cases_count=len(cases),
            case_results_count=len(case_results),
            accuracy=accuracy,
            latency_ms=latency_ms,
            gate_threshold=gate_threshold,
            gate_passed=gate_passed,
        )

    return RunOutcome(
        evaluation_name=evaluation.name,
        evaluation_id=evaluation.id,
        run_id=run.id,
        provider=provider,
        model=model,
        cases_count=len(cases),
        case_results_count=len(case_results),
        accuracy=accuracy,
        latency_ms=latency_ms,
        gate_threshold=gate_threshold,
        gate_passed=gate_passed,
        report_path=report_path,
    )


def _print_regression_summary(
    *,
    current: RunOutcome,
    baseline: RunOutcome,
) -> None:
    delta = current.accuracy - baseline.accuracy

    if delta > 0:
        status = "IMPROVED"
    elif delta < 0:
        status = "REGRESSED"
    else:
        status = "UNCHANGED"

    print()
    print("Baseline Regression Check")
    print(
        f"Baseline ({baseline.provider}:{baseline.model}): " f"{baseline.accuracy:.2f}"
    )
    print(f"Current  ({current.provider}:{current.model}): " f"{current.accuracy:.2f}")
    print(f"Delta: {delta:+.2f}")
    print(f"Result: {status}")


def run_from_yaml(config_path: str) -> int:
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
                "dataset_version_id": inputs.dataset_version_id,
                "prompt_version_id": inputs.prompt_version_id,
                "metric_plugins": [{"name": inputs.metric_name}],
            },
        )(),
    )

    print()
    print(f"Loaded {outcome.cases_count} cases")
    print(f"Created {outcome.case_results_count} case results")
    print(f"Accuracy: {outcome.accuracy:.2f}")
    print(f"Latency: {outcome.latency_ms:.0f} ms")

    if outcome.gate_threshold is None:
        print("Quality Gate: Not configured")
        exit_code = 0
    else:
        gate_status = "PASSED" if outcome.gate_passed else "FAILED"
        print(
            f"Quality Gate: {gate_status} " f"(threshold: {outcome.gate_threshold:.2f})"
        )
        exit_code = 0 if outcome.gate_passed else 1

    if inputs.baseline is not None:
        baseline_provider = (
            str(inputs.baseline.get("provider", "mock")).strip() or "mock"
        )
        baseline_model = str(inputs.baseline.get("model", "")).strip()

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

        regression_raw = inputs.regression_config.get("max_drop", 0.0)

        try:
            max_drop = float(regression_raw)
        except (TypeError, ValueError) as exc:
            raise ValueError("regression.max_drop must be a number") from exc

        if max_drop < 0:
            raise ValueError("regression.max_drop must be greater than or equal to 0")

        delta = outcome.accuracy - baseline_outcome.accuracy
        regression_passed = delta >= -max_drop

        _print_regression_summary(
            current=outcome,
            baseline=baseline_outcome,
        )

        print(f"Allowed Drop: {max_drop:.2f}")
        print("Regression Gate: " f"{'PASSED' if regression_passed else 'FAILED'}")

        if not regression_passed:
            exit_code = 1

    print()
    print("Run created successfully")
    print(f"Run ID: {outcome.run_id}")
    print("Run Status: created")

    print()
    if outcome.report_path is not None:
        print(f"Report written to: {outcome.report_path}")

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
        left_name=f"{left_outcome.provider}:{left_outcome.model}",
        right_name=f"{right_outcome.provider}:{right_outcome.model}",
        left_accuracy=left_outcome.accuracy,
        right_accuracy=right_outcome.accuracy,
    )

    print("✔ Comparison completed successfully")
    print()
    print(f"Dataset Version: {inputs.dataset_version_id}")
    print(f"Prompt Version: {inputs.prompt_version_id}")
    print()
    print(f"Left  ({comparison.left_name}): {comparison.left_accuracy:.2f}")
    print(f"Right ({comparison.right_name}): {comparison.right_accuracy:.2f}")
    print(f"Winner: {comparison.winner}")
    print(f"Margin: {comparison.margin:.2f}")

    report_path = write_comparison_report(
        "reports",
        evaluation_name=inputs.name,
        evaluation_id=left_outcome.evaluation_id,
        dataset_version=inputs.dataset_version_id,
        prompt_version=inputs.prompt_version_id,
        left_name=f"{left_outcome.provider}:{left_outcome.model}",
        right_name=f"{right_outcome.provider}:{right_outcome.model}",
        left_accuracy=left_outcome.accuracy,
        right_accuracy=right_outcome.accuracy,
        winner=comparison.winner,
        margin=comparison.margin,
    )

    print()
    print(f"Report written to: {report_path}")

    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "create-evaluation":
        use_case = create_use_case()

        evaluation = use_case.execute(
            name=args.name,
            dataset_version_id=args.dataset_version_id,
            prompt_version_id=args.prompt_version_id,
            target={"provider": args.target},
            metric_plugins=[{"name": args.metric_plugins}],
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

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
