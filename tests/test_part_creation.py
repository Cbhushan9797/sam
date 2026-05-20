from __future__ import annotations

import os
import time

from dotenv import load_dotenv
from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright

from src.pages.home_page import HomePage
from src.pages.login_page import LoginPage
from src.pages.part_creation_page import PartCreationPage
from src.pages.search_page import SearchPage
from src.use_cases.part_creation.data_reader import read_part_data
from src.use_cases.use_case_manager import get_use_case_paths
from src.utils.evidence import capture_screenshot_evidence, create_evidence_directory
from src.utils.execution_reporter import (
    ExecutionReport,
    PartExecutionResult,
    calculate_average_time,
    write_execution_report,
)
from src.utils.file_utils import ensure_directory, resolve_project_path, write_text_file


def require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing {name}. Set it in the .env file before running the Playwright test.")
    return value


def round_seconds(value: float) -> float:
    return round(value, 2)


def test_part_creation() -> None:
    load_dotenv()
    use_case_paths = get_use_case_paths("part_creation")

    teamcenter_url = require_env("TEAMCENTER_URL")
    username = require_env("TEAMCENTER_USERNAME")
    password = require_env("TEAMCENTER_PASSWORD")
    headless = os.getenv("PLAYWRIGHT_HEADLESS", "true").strip().lower() != "false"

    execution_log_path = use_case_paths.execution_log_path
    trace_output_path = resolve_project_path("test-results", "artifacts", "part_creation_trace.zip")
    part_data_rows = read_part_data(use_case_paths.input_data_path)
    results: list[PartExecutionResult] = []
    log_lines: list[str] = []
    overall_start = time.perf_counter()

    ensure_directory(trace_output_path.parent)

    def append_log(message: str) -> None:
        line = f"[{time.strftime('%Y-%m-%dT%H:%M:%S')}] {message}"
        log_lines.append(line)
        print(line)

    def build_report() -> ExecutionReport:
        passed = sum(1 for result in results if result.status == "PASSED")
        failed = sum(1 for result in results if result.status == "FAILED")
        return ExecutionReport(
            totalParts=len(part_data_rows),
            passed=passed,
            failed=failed,
            totalTimeSeconds=round_seconds(time.perf_counter() - overall_start),
            averageTimePerPartSeconds=calculate_average_time(results),
            results=results,
        )

    playwright: Playwright | None = None
    browser: Browser | None = None
    context: BrowserContext | None = None
    page: Page | None = None

    try:
        create_evidence_directory(use_case_paths.use_case_name)
        append_log(f"Loaded {len(part_data_rows)} part records.")
        append_log(f"Opening Teamcenter at {teamcenter_url}.")

        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(headless=headless)
        context = browser.new_context(base_url=teamcenter_url)
        context.set_default_timeout(60_000)
        context.set_default_navigation_timeout(90_000)
        context.tracing.start(screenshots=True, snapshots=True, sources=True)
        page = context.new_page()

        login_page = LoginPage(page)
        home_page = HomePage(page)
        part_creation_page = PartCreationPage(page)
        search_page = SearchPage(page)

        login_page.goto()
        login_page.verify_login_page_loaded()
        append_log(f"Logging in as {username}.")
        login_page.login(username, password)
        home_page.verify_home_page_loaded()
        append_log("Teamcenter home page loaded.")

        for part in part_data_rows:
            part_start = time.perf_counter()
            append_log(f"Starting part creation for {part.partId}.")

            try:
                home_page.navigate_to_part_creation()
                part_creation_page.verify_part_creation_page_loaded()
                part_creation_page.create_part(part)
                part_creation_page.save_part()
                part_creation_page.verify_part_created(part.partId)
                search_page.search_part(part.partId)
                search_page.verify_part_appears_in_results(part.partId)

                screenshot_path = capture_screenshot_evidence(
                    page,
                    use_case_paths.use_case_name,
                    f"{part.partId}_passed",
                )
                time_taken_seconds = round_seconds(time.perf_counter() - part_start)
                results.append(
                    PartExecutionResult(
                        partId=part.partId,
                        partName=part.partName,
                        partType=part.partType,
                        status="PASSED",
                        timeTakenSeconds=time_taken_seconds,
                        screenshotPath=screenshot_path,
                        errorMessage="",
                    )
                )
                append_log(f"Part {part.partId} passed in {time_taken_seconds} seconds.")
            except Exception as caught:
                error_message = str(caught)
                screenshot_path = ""
                if page is not None:
                    try:
                        screenshot_path = capture_screenshot_evidence(
                            page,
                            use_case_paths.use_case_name,
                            f"{part.partId}_failed",
                        )
                    except Exception:
                        screenshot_path = ""

                time_taken_seconds = round_seconds(time.perf_counter() - part_start)
                results.append(
                    PartExecutionResult(
                        partId=part.partId,
                        partName=part.partName,
                        partType=part.partType,
                        status="FAILED",
                        timeTakenSeconds=time_taken_seconds,
                        screenshotPath=screenshot_path,
                        errorMessage=error_message,
                    )
                )
                append_log(f"Part {part.partId} failed in {time_taken_seconds} seconds: {error_message}")

                if page is not None:
                    try:
                        append_log(f"Attempting recovery before the next part after failure on {part.partId}.")
                        page.goto(teamcenter_url, wait_until="domcontentloaded")
                        if login_page.is_visible():
                            append_log("Recovery landed on the login page. Re-authenticating.")
                            login_page.login(username, password)
                        home_page.verify_home_page_loaded()
                        append_log(f"Recovery completed after failure on {part.partId}.")
                    except Exception as recovery_error:
                        append_log(f"Recovery after {part.partId} was limited: {recovery_error}")
    except Exception as caught:
        fatal_error = str(caught)
        append_log(f"Fatal execution error: {fatal_error}")

        processed_part_ids = {result.partId for result in results}
        for part in part_data_rows:
            if part.partId in processed_part_ids:
                continue

            screenshot_path = ""
            if page is not None:
                try:
                    screenshot_path = capture_screenshot_evidence(
                        page,
                        use_case_paths.use_case_name,
                        f"{part.partId}_fatal",
                    )
                except Exception:
                    screenshot_path = ""

            results.append(
                PartExecutionResult(
                    partId=part.partId,
                    partName=part.partName,
                    partType=part.partType,
                    status="FAILED",
                    timeTakenSeconds=0,
                    screenshotPath=screenshot_path,
                    errorMessage=fatal_error,
                )
            )
    finally:
        report = build_report()
        write_execution_report(report, use_case_paths.execution_report_path)
        append_log(
            f"Execution report saved with {report.passed} passed and {report.failed} failed part results."
        )
        write_text_file(execution_log_path, "\n".join(log_lines) + "\n")

        if context is not None:
            if report.failed > 0:
                context.tracing.stop(path=str(trace_output_path))
            else:
                context.tracing.stop()
            context.close()

        if browser is not None:
            browser.close()

        if playwright is not None:
            playwright.stop()

    failed_results = [result for result in results if result.status == "FAILED"]
    assert not failed_results, (
        "One or more Teamcenter parts failed. Review "
        f"{use_case_paths.execution_report_path} and {use_case_paths.execution_log_path}."
    )
