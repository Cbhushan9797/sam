from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.test_data.csv_utils import read_csv_rows, validate_required_columns, validate_required_values
from src.use_cases.use_case_manager import get_use_case_paths


@dataclass
class BomData:
    bomId: str
    parentItemId: str
    childItemId: str
    quantity: str = ""
    unitOfMeasure: str = ""


REQUIRED_COLUMNS = ("bomId", "parentItemId", "childItemId")


def read_bom_data(csv_path: Path | None = None) -> list[BomData]:
    resolved_csv_path = csv_path or get_use_case_paths("bom_creation").input_data_path
    fieldnames, rows = read_csv_rows(resolved_csv_path)
    validate_required_columns(fieldnames, REQUIRED_COLUMNS)
    validate_required_values(rows, REQUIRED_COLUMNS)

    return [
        BomData(
            bomId=(row.get("bomId") or "").strip(),
            parentItemId=(row.get("parentItemId") or "").strip(),
            childItemId=(row.get("childItemId") or "").strip(),
            quantity=(row.get("quantity") or "").strip(),
            unitOfMeasure=(row.get("unitOfMeasure") or "").strip(),
        )
        for row in rows
    ]
