from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.test_data.csv_utils import read_csv_rows, validate_required_columns, validate_required_values
from src.use_cases.use_case_manager import get_use_case_paths


@dataclass
class PartData:
    partId: str
    partName: str
    partType: str
    description: str = ""
    revision: str = ""
    unitOfMeasure: str = ""


REQUIRED_COLUMNS = ("partId", "partName", "partType")


def read_part_data(csv_path: Path | None = None) -> list[PartData]:
    resolved_csv_path = csv_path or get_use_case_paths("part_creation").input_data_path
    fieldnames, rows = read_csv_rows(resolved_csv_path)
    validate_required_columns(fieldnames, REQUIRED_COLUMNS)
    validate_required_values(rows, REQUIRED_COLUMNS)

    return [
        PartData(
            partId=(row.get("partId") or "").strip(),
            partName=(row.get("partName") or "").strip(),
            partType=(row.get("partType") or "").strip(),
            description=(row.get("description") or "").strip(),
            revision=(row.get("revision") or "").strip(),
            unitOfMeasure=(row.get("unitOfMeasure") or "").strip(),
        )
        for row in rows
    ]
