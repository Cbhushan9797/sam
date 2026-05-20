from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def resolve_project_path(*segments: str) -> Path:
    return PROJECT_ROOT.joinpath(*segments)


def ensure_directory(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def file_exists(path: Path) -> bool:
    return path.exists()


def read_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text_file(path: Path, content: str) -> None:
    ensure_directory(path.parent)
    path.write_text(content, encoding="utf-8")


def read_json_file(path: Path) -> Any:
    return json.loads(read_text_file(path))


def write_json_file(path: Path, data: Any) -> None:
    ensure_directory(path.parent)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
