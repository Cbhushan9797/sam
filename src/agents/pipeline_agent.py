from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

from src.use_cases.use_case_manager import get_use_case_paths, parse_use_case_args
from src.utils.file_utils import PROJECT_ROOT
from src.utils.logger import error, info, warn


@dataclass
class StageResult:
    label: str
    command: list[str]
    returncode: int
    stdout: str
    stderr: str


class PipelineStageError(RuntimeError):
    def __init__(self, stage_result: StageResult) -> None:
        super().__init__(f"Stage failed: {stage_result.label}")
        self.stage_result = stage_result


def run_stage(label: str, command: list[str], cwd: Path) -> StageResult:
    info(f"Starting stage: {label}")
    result = subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    stage_result = StageResult(
        label=label,
        command=command,
        returncode=result.returncode,
        stdout=result.stdout,
        stderr=result.stderr,
    )

    print(f"\n=== {label} ===")
    print(f"Command: {' '.join(command)}")
    if stage_result.stdout.strip():
        print(stage_result.stdout.rstrip())
    if stage_result.stderr.strip():
        print(stage_result.stderr.rstrip(), file=sys.stderr)

    if stage_result.returncode == 0:
        info(f"Stage completed: {label}")
        return stage_result

    error(f"Stage failed: {label} (exit code {stage_result.returncode})")
    raise PipelineStageError(stage_result)


def main() -> None:
    load_dotenv()
    args = parse_use_case_args("Run the end-to-end Teamcenter AI automation pipeline for a selected use case.")
    use_case_paths = get_use_case_paths(args.use_case)

    use_case_args = ["--use-case", use_case_paths.use_case_name]
    stages = [
        ("Generate Test Plan", [sys.executable, "-m", "src.agents.planner_agent", *use_case_args]),
        (
            "Capture Playwright MCP Snapshot",
            [sys.executable, "-m", "src.agents.mcp_snapshot_agent", *use_case_args],
        ),
        (
            "Generate Locator Candidates",
            [sys.executable, "-m", "src.agents.locator_agent", *use_case_args],
        ),
        (
            "Generate Playwright Code",
            [sys.executable, "-m", "src.agents.generator_agent", *use_case_args],
        ),
        (
            "Run Playwright Test",
            [sys.executable, "-m", "pytest", str(use_case_paths.stable_test_path), "-s"],
        ),
    ]

    info(f"Running full automation pipeline for use case `{use_case_paths.use_case_name}`.")
    try:
        for label, command in stages[:-1]:
            run_stage(label, command, PROJECT_ROOT)

        try:
            run_stage(stages[-1][0], stages[-1][1], PROJECT_ROOT)
        except PipelineStageError as caught:
            warn(
                "Stable Playwright execution failed. Triggering the healer agent automatically "
                "to capture suggested fixes."
            )
            try:
                run_stage(
                    "Generate Healing Suggestions",
                    [sys.executable, "-m", "src.agents.healer_agent", *use_case_args],
                    PROJECT_ROOT,
                )
            except PipelineStageError:
                warn("Healing suggestions could not be generated after the failed test run.")
            raise caught

        info("Full automation pipeline completed successfully.")
    except PipelineStageError as caught:
        raise SystemExit(caught.stage_result.returncode) from caught


if __name__ == "__main__":
    main()
