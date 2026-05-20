from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PATHS = [
    Path("streamlit_app.py"),
    Path("requirements.txt"),
    Path("README.md"),
    Path("docs/project-architecture.md"),
    Path("docs/use-case-development-guide.md"),
    Path("docs/copilot-working-guide.md"),
    Path("docs/run-on-new-computer.md"),
    Path("src/use_cases/use_case_manager.py"),
    Path("src/use_cases/part_creation/config.json"),
    Path("src/use_cases/part_creation/manual_steps.txt"),
    Path("src/use_cases/part_creation/input_data.csv"),
    Path("src/use_cases/part_creation/data_reader.py"),
    Path("src/use_cases/bom_creation/config.json"),
    Path("src/use_cases/bom_creation/manual_steps.txt"),
    Path("src/use_cases/bom_creation/input_data.csv"),
    Path("src/use_cases/bom_creation/data_reader.py"),
    Path("src/agents/planner_agent.py"),
    Path("src/agents/pipeline_agent.py"),
    Path("src/agents/mcp_snapshot_agent.py"),
    Path("src/agents/locator_agent.py"),
    Path("src/agents/generator_agent.py"),
    Path("src/agents/healer_agent.py"),
    Path("src/llm/ollama_client.py"),
    Path("src/llm/prompts.py"),
    Path("src/knowledge/locator_registry.py"),
    Path("src/knowledge/locator-registry/README.md"),
    Path("src/knowledge/locator-registry/default/teamcenter_generic/locator-registry.json"),
    Path("src/knowledge/locator-registry/default/teamcenter_generic/locator-notes.md"),
    Path("src/mcp/playwright_mcp_client.py"),
    Path("src/mcp/snapshot_artifact.py"),
    Path("src/pages/login_page.py"),
    Path("src/pages/home_page.py"),
    Path("src/pages/part_creation_page.py"),
    Path("src/pages/search_page.py"),
    Path("src/test_data/csv_utils.py"),
    Path("src/utils/file_utils.py"),
    Path("src/utils/locator_builder.py"),
    Path("src/utils/locator_resolver.py"),
    Path("src/utils/evidence.py"),
    Path("src/utils/execution_reporter.py"),
    Path("src/utils/logger.py"),
    Path("tests/test_part_creation.py"),
    Path("tests/test_bom_creation.py"),
]

FORBIDDEN_PATHS = [
    Path("package.json"),
    Path("tsconfig.json"),
    Path("playwright.config.ts"),
    Path("src/generated"),
    Path("src/manual-tests"),
    Path("src/input-data"),
]

FORBIDDEN_SUFFIXES = {".ts", ".tsx", ".js", ".jsx"}
SKIP_DIR_NAMES = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    "node_modules",
    "playwright-report",
    "test-results",
}


def collect_python_files(folder: Path) -> list[Path]:
    if not folder.exists():
        return []
    return sorted(path for path in folder.iterdir() if path.is_file() and path.suffix == ".py")


def should_skip_path(path: Path) -> bool:
    return any(part in SKIP_DIR_NAMES for part in path.parts)


def main() -> int:
    errors: list[str] = []

    for relative_path in REQUIRED_PATHS:
        if not (PROJECT_ROOT / relative_path).exists():
            errors.append(f"Missing required path: {relative_path.as_posix()}")

    for relative_path in FORBIDDEN_PATHS:
        if (PROJECT_ROOT / relative_path).exists():
            errors.append(f"Forbidden file exists: {relative_path.as_posix()}")

    for path in PROJECT_ROOT.rglob("*"):
        if should_skip_path(path.relative_to(PROJECT_ROOT)):
            continue

        if not path.is_file():
            continue

        if path.suffix in FORBIDDEN_SUFFIXES:
            errors.append(f"Forbidden non-Python source file found: {path.relative_to(PROJECT_ROOT).as_posix()}")

    for file_path in collect_python_files(PROJECT_ROOT / "src" / "agents"):
        if file_path.name == "__init__.py":
            continue
        if not file_path.name.endswith("_agent.py"):
            errors.append(f"Agent file must end with _agent.py: {file_path.relative_to(PROJECT_ROOT).as_posix()}")

    for file_path in collect_python_files(PROJECT_ROOT / "src" / "pages"):
        if file_path.name == "__init__.py":
            continue
        if not file_path.name.endswith("_page.py"):
            errors.append(f"Page file must end with _page.py: {file_path.relative_to(PROJECT_ROOT).as_posix()}")

    for file_path in collect_python_files(PROJECT_ROOT / "tests"):
        if not file_path.name.startswith("test_"):
            errors.append(f"Test file must start with test_: {file_path.relative_to(PROJECT_ROOT).as_posix()}")

    for use_case_root in sorted((PROJECT_ROOT / "src" / "use_cases").glob("*")):
        if not use_case_root.is_dir() or use_case_root.name == "__pycache__":
            continue

        config_path = use_case_root / "config.json"
        manual_steps_path = use_case_root / "manual_steps.txt"
        input_data_path = use_case_root / "input_data.csv"
        generated_dir = use_case_root / "generated"

        if not config_path.exists():
            errors.append(f"Use case is missing config.json: {use_case_root.relative_to(PROJECT_ROOT).as_posix()}")
        if not manual_steps_path.exists():
            errors.append(
                f"Use case is missing manual_steps.txt: {use_case_root.relative_to(PROJECT_ROOT).as_posix()}"
            )
        if not input_data_path.exists():
            errors.append(
                f"Use case is missing input_data.csv: {use_case_root.relative_to(PROJECT_ROOT).as_posix()}"
            )
        if not generated_dir.exists():
            errors.append(f"Use case is missing generated/: {use_case_root.relative_to(PROJECT_ROOT).as_posix()}")

    if errors:
        print("Project structure validation failed:\n")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Project structure validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
