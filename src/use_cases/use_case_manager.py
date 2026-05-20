from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.utils.file_utils import resolve_project_path


DEFAULT_USE_CASE = "part_creation"
USE_CASES_ROOT = resolve_project_path("src", "use_cases")


@dataclass
class UseCasePaths:
    use_case_name: str
    use_case_root: Path
    config_path: Path
    manual_steps_path: Path
    input_data_path: Path
    generated_dir: Path
    test_plan_path: Path
    mcp_snapshot_path: Path
    locator_candidates_path: Path
    generated_code_path: Path
    healing_suggestions_path: Path
    execution_report_path: Path
    execution_log_path: Path
    stable_test_path: Path


def get_active_use_case(explicit_use_case: str | None = None) -> str:
    selected = explicit_use_case or os.getenv("TEAMCENTER_USE_CASE", DEFAULT_USE_CASE)
    return selected.strip() or DEFAULT_USE_CASE


def get_use_case_root(use_case_name: str | None = None) -> Path:
    return USE_CASES_ROOT / get_active_use_case(use_case_name)


def get_use_case_config_path(use_case_name: str | None = None) -> Path:
    return get_use_case_root(use_case_name) / "config.json"


def load_use_case_config(use_case_name: str | None = None) -> dict[str, Any]:
    config_path = get_use_case_config_path(use_case_name)
    if not config_path.exists():
        raise FileNotFoundError(f"Use-case config not found: {config_path}")

    return json.loads(config_path.read_text(encoding="utf-8"))


def get_use_case_paths(use_case_name: str | None = None) -> UseCasePaths:
    selected = get_active_use_case(use_case_name)
    root = get_use_case_root(selected)
    config = load_use_case_config(selected)
    generated_dir = root / "generated"
    stable_test_path = resolve_project_path(config["stableTestPath"])

    return UseCasePaths(
        use_case_name=selected,
        use_case_root=root,
        config_path=get_use_case_config_path(selected),
        manual_steps_path=root / "manual_steps.txt",
        input_data_path=root / "input_data.csv",
        generated_dir=generated_dir,
        test_plan_path=generated_dir / "testPlan.md",
        mcp_snapshot_path=generated_dir / "playwrightMcpSnapshot.md",
        locator_candidates_path=generated_dir / "locatorCandidates.md",
        generated_code_path=generated_dir / "generated_playwright.py",
        healing_suggestions_path=generated_dir / "healingSuggestions.md",
        execution_report_path=generated_dir / "executionReport.json",
        execution_log_path=generated_dir / "testExecution.log",
        stable_test_path=stable_test_path,
    )


def list_available_use_cases() -> list[dict[str, Any]]:
    use_cases: list[dict[str, Any]] = []
    if not USE_CASES_ROOT.exists():
        return use_cases

    for config_path in sorted(USE_CASES_ROOT.glob("*/config.json")):
        config = json.loads(config_path.read_text(encoding="utf-8"))
        use_cases.append(config)

    return use_cases


def parse_use_case_args(description: str) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--use-case",
        default=os.getenv("TEAMCENTER_USE_CASE", DEFAULT_USE_CASE),
        help="Use-case identifier under src/use_cases/.",
    )
    return parser.parse_args()
