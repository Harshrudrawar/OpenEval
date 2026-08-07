from __future__ import annotations

import argparse
from typing import Any

from openeval.application import (
    CreateEvaluationDefinitionUseCase,
    CreateRunUseCase,
    LoadCasesFromDatasetUseCase,
)
from openeval.infrastructure import (
    CsvDatasetLoader,
    InMemoryEvaluationRepository,
    InMemoryRunRepository,
)
from openeval.interface.yaml_loader import load_yaml


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
    run_parser.add_argument("config_path", help="Path to evaluation YAML file")

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


def run_from_yaml(config_path: str) -> int:
    config = load_yaml(config_path)

    name = config.get("name", "")
    dataset_config = config.get("dataset", {})
    prompt_config = config.get("prompt", {})
    target = config.get("target", {})
    metrics = config.get("metrics", [])

    if not isinstance(dataset_config, dict):
        raise ValueError("dataset must be a YAML mapping/object")

    if not isinstance(prompt_config, dict):
        raise ValueError("prompt must be a YAML mapping/object")

    if not isinstance(target, dict):
        raise ValueError("target must be a YAML mapping/object")

    if not isinstance(metrics, list):
        raise ValueError("metrics must be a YAML list")

    dataset_path = dataset_config.get("path", "")
    if not isinstance(dataset_path, str) or not dataset_path.strip():
        raise ValueError("dataset.path must be a non-empty string")

    dataset_version_id = dataset_config.get("version", "")
    if not isinstance(dataset_version_id, str) or not dataset_version_id.strip():
        raise ValueError("dataset.version must be a non-empty string")

    prompt_version_id = prompt_config.get("version", "")
    if not isinstance(prompt_version_id, str) or not prompt_version_id.strip():
        raise ValueError("prompt.version must be a non-empty string")

    metric_plugins = [{"name": metric} for metric in metrics]

    evaluation_use_case = create_use_case()
    evaluation = evaluation_use_case.execute(
        name=name,
        dataset_version_id=dataset_version_id,
        prompt_version_id=prompt_version_id,
        target=target,
        metric_plugins=metric_plugins,
    )

    dataset_loader = CsvDatasetLoader()
    load_cases_use_case = LoadCasesFromDatasetUseCase(dataset_loader)
    cases = load_cases_use_case.execute(
        dataset_path=dataset_path,
        evaluation_definition_id=evaluation.id,
    )

    run_repository = InMemoryRunRepository()
    run_use_case = CreateRunUseCase(run_repository)
    run = run_use_case.execute(evaluation.id)

    print_evaluation_summary(evaluation)
    print()
    print(f"Loaded {len(cases)} cases")
    print()
    print("Run created successfully")
    print(f"Run ID: {run.id}")
    print(f"Run Status: {run.status}")

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

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
