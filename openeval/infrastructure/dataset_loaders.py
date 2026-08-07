from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from openeval.application.ports import DatasetLoader


class CsvDatasetLoader(DatasetLoader):
    def load_rows(self, path: str) -> list[dict[str, Any]]:
        csv_path = Path(path)

        with csv_path.open("r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)
            return [dict(row) for row in reader]
