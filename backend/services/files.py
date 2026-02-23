from pathlib import Path
import shutil
from typing import Dict, Any

import backend.config as config

TESTS_DIR: Path = config.TESTS_DIR
TESTS_DIR.mkdir(parents=True, exist_ok=True)

def clean_tests_directory() -> Dict[str, Any] | None:
    TESTS_DIR.mkdir(parents=True, exist_ok=True)
    for entry in TESTS_DIR.iterdir():
        try:
            if entry.is_file() or entry.is_symlink():
                entry.unlink()
            elif entry.is_dir():
                shutil.rmtree(entry, ignore_errors=True)
        except Exception as e:
            return {
                "error": f"Failed to clean tests directory: {e}",
                "failed_path": str(entry),
            }
    return None

def save_generated_test(test: str) -> str:
    """Save the generated Playwright test as tests/test.spec.js"""
    clean_tests_directory()
    try:
        dest = TESTS_DIR / "test.spec.js"
        with open(dest, "w", encoding="utf-8") as f:
            f.write(test)
        return "file saved successfully"
    except Exception as e:
        return f"file was not saved due to {e}"

def save_uploaded_as_canonical_test(file_bytes: bytes, filename: str) -> dict:
    """Overwrite tests/test.spec.js with uploaded bytes."""
    if isinstance(file_bytes, str):
        file_bytes = file_bytes.encode("utf-8", errors="ignore")
    dest = TESTS_DIR / "test.spec.js"
    dest.write_bytes(file_bytes)
    return {"status": "ok", "saved_as": str(dest), "size_bytes": len(file_bytes)}