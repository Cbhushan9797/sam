from __future__ import annotations

import csv
from pathlib import Path


def read_csv_rows(csv_path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with csv_path.open("r", encoding="utf-8-sig", newline="") as file_handle:
        reader = csv.DictReader(file_handle)
        fieldnames = reader.fieldnames or []
        rows = list(reader)

    return fieldnames, rows


def validate_required_columns(fieldnames: list[str], required_columns: tuple[str, ...]) -> None:
    missing_columns = [column for column in required_columns if column not in fieldnames]
    if missing_columns:
        raise ValueError(f"Missing required CSV columns: {', '.join(missing_columns)}.")


def validate_required_values(rows: list[dict[str, str]], required_columns: tuple[str, ...]) -> None:
    if not rows:
        raise ValueError("CSV file does not contain any data rows.")

    for index, row in enumerate(rows, start=2):
        for required_column in required_columns:
            value = (row.get(required_column) or "").strip()
            if not value:
                raise ValueError(
                    f'CSV row {index} has an empty required value for column "{required_column}".'
                )
