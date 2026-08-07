from __future__ import annotations

from dataclasses import dataclass

from openeval.application.ports import DatasetLoader
from openeval.domain.cases import Case
from openeval.domain.shared import generate_id


@dataclass
class LoadCasesFromDatasetUseCase:
    dataset_loader: DatasetLoader

    def execute(
        self, *, dataset_path: str, evaluation_definition_id: str
    ) -> list[Case]:
        rows = self.dataset_loader.load_rows(dataset_path)
        cases: list[Case] = []

        for row in rows:
            input_value = row.get("input", "")
            expected_value = row.get("expected_output", "")

            case = Case(
                id=generate_id(),
                evaluation_definition_id=evaluation_definition_id,
                input_data={"input": input_value},
                expected_output={"expected_output": expected_value},
            )
            cases.append(case)

        return cases
