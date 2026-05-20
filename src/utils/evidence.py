from __future__ import annotations

import re
from pathlib import Path

from playwright.sync_api import Page

from .file_utils import PROJECT_ROOT, ensure_directory, resolve_project_path

EVIDENCE_ROOT = resolve_project_path("test-results", "evidence")


def create_evidence_directory(use_case_name: str) -> Path:
    return ensure_directory(EVIDENCE_ROOT / use_case_name)


def to_safe_file_name(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]+", "_", value).strip("_") or "evidence"


def capture_screenshot_evidence(page: Page, use_case_name: str, file_stem: str) -> str:
    directory = create_evidence_directory(use_case_name)
    file_name = f"{to_safe_file_name(file_stem)}.png"
    absolute_path = directory / file_name
    page.screenshot(path=str(absolute_path), full_page=True)
    return absolute_path.relative_to(PROJECT_ROOT).as_posix()
