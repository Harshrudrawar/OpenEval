from __future__ import annotations

import argparse

from openeval.application import CreateEvaluationDefinitionUseCase
from openeval.infrastructure import InMemoryEvaluationRepository


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

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "create-evaluation":
        repository = InMemoryEvaluationRepository()
        use_case = CreateEvaluationDefinitionUseCase(repository)

        evaluation = use_case.execute(
            name=args.name,
            dataset_version_id=args.dataset_version_id,
            prompt_version_id=args.prompt_version_id,
            target={"provider": args.target},
            metric_plugins=[{"name": args.metric_plugins}],
        )

        print("✔ Evaluation created successfully")
        print()
        print(f"ID: {evaluation.id}")
        print(f"Name: {evaluation.name}")
        print(f"Dataset Version: {evaluation.dataset_version_id}")
        print(f"Prompt Version: {evaluation.prompt_version_id}")
        print(f"Metrics: {len(evaluation.metric_plugins)}")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())