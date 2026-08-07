from __future__ import annotations

from pathlib import Path

from openeval.infrastructure.dataset_loaders import CsvDatasetLoader


def test_csv_dataset_loader_reads_rows(tmp_path: Path) -> None:
    csv_file = tmp_path / "dataset.csv"
    csv_file.write_text(
        "input,expected_output\n" '"Hello","Hi"\n' '"What is 2 + 2?","4"\n',
        encoding="utf-8",
    )

    loader = CsvDatasetLoader()
    rows = loader.load_rows(str(csv_file))

    assert len(rows) == 2
    assert rows[0]["input"] == "Hello"
    assert rows[0]["expected_output"] == "Hi"
