from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from src.utils.file_utils import resolve_project_path


DEFAULT_LOCATOR_PROFILE = "default/teamcenter_generic"
LOCATOR_REGISTRY_ROOT = resolve_project_path("src", "knowledge", "locator-registry")


def get_locator_profile() -> str:
    return os.getenv("TEAMCENTER_LOCATOR_PROFILE", DEFAULT_LOCATOR_PROFILE).strip() or DEFAULT_LOCATOR_PROFILE


def get_profile_directory(profile: str | None = None) -> Path:
    selected_profile = (profile or get_locator_profile()).replace("\\", "/").strip("/")
    return LOCATOR_REGISTRY_ROOT.joinpath(*selected_profile.split("/"))


def get_registry_file_path(profile: str | None = None) -> Path:
    return get_profile_directory(profile) / "locator-registry.json"


def get_registry_notes_path(profile: str | None = None) -> Path:
    return get_profile_directory(profile) / "locator-notes.md"


def load_locator_registry(profile: str | None = None) -> dict[str, Any]:
    registry_path = get_registry_file_path(profile)
    if not registry_path.exists():
        return {}

    return json.loads(registry_path.read_text(encoding="utf-8"))


def load_locator_notes(profile: str | None = None) -> str:
    notes_path = get_registry_notes_path(profile)
    if not notes_path.exists():
        return "No locator notes file was found for the selected profile."

    return notes_path.read_text(encoding="utf-8")


def get_registry_locator(page_name: str, locator_name: str, profile: str | None = None) -> dict[str, Any] | None:
    registry = load_locator_registry(profile)
    return registry.get("pages", {}).get(page_name, {}).get(locator_name)


def build_registry_prompt_context(profile: str | None = None) -> str:
    selected_profile = profile or get_locator_profile()
    registry = load_locator_registry(selected_profile)
    notes = load_locator_notes(selected_profile)

    if not registry:
        return (
            f"No structured locator registry file was found for profile `{selected_profile}`.\n\n"
            f"## Locator Notes\n{notes}"
        )

    registry_json = json.dumps(registry, indent=2)
    return "\n".join(
        [
            f"## Locator Profile\n{selected_profile}",
            "",
            "## Structured Locator Registry",
            registry_json,
            "",
            "## Human Readable Locator Notes",
            notes,
        ]
    )
