from __future__ import annotations

from datetime import datetime


def _timestamp() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def info(message: str) -> None:
    print(f"[INFO] [{_timestamp()}] {message}")


def warn(message: str) -> None:
    print(f"[WARN] [{_timestamp()}] {message}")


def error(message: str) -> None:
    print(f"[ERROR] [{_timestamp()}] {message}")
