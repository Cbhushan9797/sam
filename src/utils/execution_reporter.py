from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .file_utils import file_exists, read_json_file, write_json_file


@dataclass
class PartExecutionResult:
    partId: str
    partName: str
    partType: str
    status: str
    timeTakenSeconds: float
    screenshotPath: str
    errorMessage: str


@dataclass
class ExecutionReport:
    totalParts: int
    passed: int
    failed: int
    totalTimeSeconds: float
    averageTimePerPartSeconds: float
    results: list[PartExecutionResult]


def calculate_average_time(results: list[PartExecutionResult]) -> float:
    if not results:
        return 0.0

    total = sum(result.timeTakenSeconds for result in results)
    return round(total / len(results), 2)


def write_execution_report(report: ExecutionReport, output_path: Path) -> None:
    payload: dict[str, Any] = {
        "totalParts": report.totalParts,
        "passed": report.passed,
        "failed": report.failed,
        "totalTimeSeconds": report.totalTimeSeconds,
        "averageTimePerPartSeconds": report.averageTimePerPartSeconds,
        "results": [asdict(result) for result in report.results],
    }
    write_json_file(output_path, payload)


def read_execution_report(report_path: Path) -> ExecutionReport | None:
    if not file_exists(report_path):
        return None

    payload = read_json_file(report_path)
    results = [PartExecutionResult(**item) for item in payload.get("results", [])]
    return ExecutionReport(
        totalParts=payload.get("totalParts", 0),
        passed=payload.get("passed", 0),
        failed=payload.get("failed", 0),
        totalTimeSeconds=payload.get("totalTimeSeconds", 0),
        averageTimePerPartSeconds=payload.get("averageTimePerPartSeconds", 0),
        results=results,
    )
