from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from src.use_cases.use_case_manager import (
    DEFAULT_USE_CASE,
    get_use_case_paths,
    list_available_use_cases,
)

PROJECT_ROOT = Path(__file__).resolve().parent

GENERATED_FILE_BUILDERS = {
    "Test Plan": lambda paths: paths.test_plan_path,
    "Playwright MCP Snapshot": lambda paths: paths.mcp_snapshot_path,
    "Locator Candidates": lambda paths: paths.locator_candidates_path,
    "Generated Playwright Code": lambda paths: paths.generated_code_path,
    "Healing Suggestions": lambda paths: paths.healing_suggestions_path,
}
PIPELINE_LABEL = "Run Full AI Automation Pipeline"
MANUAL_COMMAND_LABELS = [
    "Generate Test Plan",
    "Capture Playwright MCP Snapshot",
    "Generate Locator Candidates",
    "Generate Playwright Code",
    "Run Playwright Test",
    "Generate Healing Suggestions",
]


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def save_uploaded_file(uploaded_file: Any, destination: Path, text_mode: bool) -> None:
    ensure_parent(destination)
    if text_mode:
        destination.write_text(uploaded_file.getvalue().decode("utf-8"), encoding="utf-8")
    else:
        destination.write_bytes(uploaded_file.getvalue())


def run_command(command: list[str]) -> dict[str, Any]:
    try:
        result = subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except FileNotFoundError as caught:
        return {
            "command": " ".join(command),
            "returncode": 1,
            "stdout": "",
            "stderr": f"Command not found: {caught}",
        }

    return {
        "command": " ".join(command),
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def build_command_map(use_case_name: str, stable_test_path: Path) -> dict[str, list[str]]:
    use_case_args = ["--use-case", use_case_name]
    return {
        PIPELINE_LABEL: [sys.executable, "-m", "src.agents.pipeline_agent", *use_case_args],
        "Generate Test Plan": [sys.executable, "-m", "src.agents.planner_agent", *use_case_args],
        "Capture Playwright MCP Snapshot": [
            sys.executable,
            "-m",
            "src.agents.mcp_snapshot_agent",
            *use_case_args,
        ],
        "Generate Locator Candidates": [
            sys.executable,
            "-m",
            "src.agents.locator_agent",
            *use_case_args,
        ],
        "Generate Playwright Code": [
            sys.executable,
            "-m",
            "src.agents.generator_agent",
            *use_case_args,
        ],
        "Run Playwright Test": [sys.executable, "-m", "pytest", str(stable_test_path), "-s"],
        "Generate Healing Suggestions": [
            sys.executable,
            "-m",
            "src.agents.healer_agent",
            *use_case_args,
        ],
    }


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def show_generated_file(label: str, path: Path) -> None:
    with st.expander(f"{label}: {path.relative_to(PROJECT_ROOT)}", expanded=False):
        if not path.exists():
            st.info("File not generated yet.")
            return

        content = read_text(path)
        if path.suffix == ".py":
            st.code(content, language="python")
        elif path.suffix == ".json":
            st.code(content, language="json")
        else:
            st.markdown(content)


def load_report(report_path: Path) -> dict[str, Any] | None:
    if not report_path.exists():
        return None

    try:
        return json.loads(report_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as caught:
        st.error(f"Unable to parse execution report: {caught}")
        return None


def show_metrics(report: dict[str, Any], total_label: str) -> None:
    metric_columns = st.columns(5)
    metric_columns[0].metric(total_label, report.get("totalParts", 0))
    metric_columns[1].metric("Passed", report.get("passed", 0))
    metric_columns[2].metric("Failed", report.get("failed", 0))
    metric_columns[3].metric("Total Time Taken", f"{report.get('totalTimeSeconds', 0)} s")
    metric_columns[4].metric(
        "Average Time Per Record",
        f"{report.get('averageTimePerPartSeconds', 0)} s",
    )


def show_result_table(report: dict[str, Any], column_labels: dict[str, str]) -> None:
    rows = report.get("results", [])
    if not rows:
        st.info("No execution results available yet.")
        return

    dataframe = pd.DataFrame(rows)
    if dataframe.empty:
        st.info("No execution results available yet.")
        return

    renamed = dataframe.rename(columns=column_labels)
    st.dataframe(renamed, use_container_width=True)

    screenshot_paths = []
    if "Screenshot Path" in renamed.columns:
        screenshot_paths = [
            str(path_value)
            for path_value in renamed["Screenshot Path"].tolist()
            if str(path_value).strip()
        ]
    if screenshot_paths:
        st.subheader("Evidence Screenshot Paths")
        for screenshot_path in screenshot_paths:
            st.write(screenshot_path)


st.set_page_config(page_title="Teamcenter AI Playwright Automation", layout="wide")
st.title("Teamcenter AI Playwright Automation")
st.caption(
    "Upload Teamcenter use-case inputs, then run one connected AI-to-Playwright pipeline with required MCP grounding."
)

st.session_state.setdefault("command_results_by_use_case", {})
available_use_cases = list_available_use_cases()
use_case_options = {
    use_case["displayName"]: use_case["id"] for use_case in available_use_cases
} or {"Part Creation": DEFAULT_USE_CASE}
selected_display_name = st.selectbox(
    "Select Teamcenter Use Case",
    options=list(use_case_options.keys()),
)
selected_use_case = use_case_options[selected_display_name]
selected_paths = get_use_case_paths(selected_use_case)
selected_config = next(
    (
        use_case
        for use_case in available_use_cases
        if use_case.get("id") == selected_use_case
    ),
    {
        "id": selected_use_case,
        "displayName": selected_display_name,
        "description": "No use-case description was found.",
        "stableTestPath": selected_paths.stable_test_path.relative_to(PROJECT_ROOT).as_posix(),
    },
)
command_map = build_command_map(selected_use_case, selected_paths.stable_test_path)

st.info(
    "\n".join(
        [
            f"Use Case ID: `{selected_config['id']}`",
            f"Description: {selected_config['description']}",
            f"Stable Test: `{selected_config['stableTestPath']}`",
        ]
    )
)

uploaded_manual_steps = st.file_uploader(
    f"Upload {selected_display_name} manual test steps file",
    type=["txt", "md"],
    key=f"manual_steps_uploader_{selected_use_case}",
)
if uploaded_manual_steps is not None:
    save_uploaded_file(uploaded_manual_steps, selected_paths.manual_steps_path, text_mode=True)
    st.success(f"Saved manual steps to {selected_paths.manual_steps_path.relative_to(PROJECT_ROOT)}")

uploaded_csv = st.file_uploader(
    f"Upload {selected_display_name} CSV input file",
    type=["csv"],
    key=f"csv_uploader_{selected_use_case}",
)
if uploaded_csv is not None:
    save_uploaded_file(uploaded_csv, selected_paths.input_data_path, text_mode=False)
    st.success(f"Saved CSV data to {selected_paths.input_data_path.relative_to(PROJECT_ROOT)}")

if selected_paths.input_data_path.exists():
    st.subheader("CSV Preview")
    try:
        csv_preview = pd.read_csv(selected_paths.input_data_path)
        st.dataframe(csv_preview, use_container_width=True)
    except Exception as caught:
        st.error(f"Unable to preview CSV: {caught}")

use_case_results = st.session_state["command_results_by_use_case"].setdefault(selected_use_case, {})
st.subheader("Pipeline")
st.write(
    "This runs the planner, required MCP snapshot, locator generation, code generation, "
    "stable Playwright test, and automatic healing on test failure."
)
if st.button(PIPELINE_LABEL, use_container_width=True, type="primary"):
    use_case_results[PIPELINE_LABEL] = run_command(command_map[PIPELINE_LABEL])

with st.expander("Advanced Manual Stage Controls", expanded=False):
    st.caption("Use these only when you want to rerun a single stage for debugging.")
    button_columns = st.columns(3)
    for index, label in enumerate(MANUAL_COMMAND_LABELS):
        if button_columns[index % 3].button(label, use_container_width=True):
            use_case_results[label] = run_command(command_map[label])

if use_case_results:
    st.subheader("Command Output Logs")
    for label, result in use_case_results.items():
        with st.expander(f"{label} ({result['command']})", expanded=False):
            if result["stdout"].strip():
                st.code(result["stdout"], language="text")
            if result["stderr"].strip():
                st.code(result["stderr"], language="text")
            if result["returncode"] == 0:
                st.success("Command completed successfully.")
            else:
                st.warning(f"Command exited with code {result['returncode']}.")

st.subheader("Generated Files")
for label, builder in GENERATED_FILE_BUILDERS.items():
    show_generated_file(label, builder(selected_paths))

report = load_report(selected_paths.execution_report_path)
if report is not None:
    st.subheader("Execution Summary")
    show_metrics(report, f"Total {selected_config.get('recordPluralLabel', selected_display_name)}")
    show_result_table(
        report,
        selected_config.get(
            "resultColumnLabels",
            {
                "status": "Status",
                "timeTakenSeconds": "Time Taken Seconds",
                "screenshotPath": "Screenshot Path",
                "errorMessage": "Error Message",
            },
        ),
    )
