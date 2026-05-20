from __future__ import annotations

import os
from datetime import datetime, timezone

from dotenv import load_dotenv

from src.mcp.playwright_mcp_client import McpClientError, PlaywrightMcpClient
from src.use_cases.use_case_manager import get_use_case_paths, parse_use_case_args
from src.utils.file_utils import write_text_file
from src.utils.logger import error, info


def _enabled() -> bool:
    return os.getenv("PLAYWRIGHT_MCP_ENABLED", "false").strip().lower() == "true"


def _target_url() -> str:
    return os.getenv("PLAYWRIGHT_MCP_TARGET_URL", "").strip() or os.getenv("TEAMCENTER_URL", "").strip()


def main() -> None:
    load_dotenv()
    args = parse_use_case_args("Capture a required Playwright MCP snapshot for a selected use case.")
    use_case_paths = get_use_case_paths(args.use_case)
    output_path = use_case_paths.mcp_snapshot_path

    if not _enabled():
        raise RuntimeError(
            "PLAYWRIGHT_MCP_ENABLED is false. Playwright MCP is required in this project. "
            "Set `PLAYWRIGHT_MCP_ENABLED=true` in .env and rerun the snapshot agent."
        )

    target_url = _target_url()
    if not target_url:
        raise RuntimeError(
            "Missing PLAYWRIGHT_MCP_TARGET_URL and TEAMCENTER_URL. Set one of them in .env."
        )

    info(f"Capturing Playwright MCP snapshot for {target_url}")
    with PlaywrightMcpClient.from_env() as mcp_client:
        snapshot = mcp_client.capture_snapshot(target_url)

    tool_names = sorted(tool.get("name", "") for tool in snapshot["tools"] if tool.get("name"))
    notifications = snapshot.get("notifications", [])
    stderr_lines = snapshot.get("stderr", [])

    markdown_lines = [
        "# Playwright MCP Snapshot",
        "",
        f"- Captured At: {datetime.now(timezone.utc).isoformat()}",
        f"- Target URL: {target_url}",
        f"- MCP Server: {snapshot.get('serverInfo', {}).get('name', 'unknown')}",
        f"- MCP Server Version: {snapshot.get('serverInfo', {}).get('version', 'unknown')}",
        "",
        "## Available Tools",
        "",
    ]
    markdown_lines.extend(f"- {name}" for name in tool_names)
    if not tool_names:
        markdown_lines.append("- None")

    markdown_lines.extend(
        [
            "",
            "## Navigation Result",
            "",
            snapshot["navigate"].text_content or "No navigation text content returned.",
            "",
            "## Accessibility Snapshot",
            "",
            snapshot["snapshot"].text_content or "No snapshot text content returned.",
            "",
            "## MCP Notifications",
            "",
        ]
    )
    markdown_lines.extend(f"- {notification.get('method', 'unknown')}" for notification in notifications)
    if not notifications:
        markdown_lines.append("- None")

    markdown_lines.extend(
        [
            "",
            "## MCP Stderr",
            "",
        ]
    )
    markdown_lines.extend(f"- {line}" for line in stderr_lines[-20:])
    if not stderr_lines:
        markdown_lines.append("- None")

    markdown_lines.extend(
        [
            "",
            "## Notes",
            "",
            "- If the snapshot only shows the login page, sign in within the MCP browser profile and rerun this agent.",
            "- Use this file as live locator context before updating page objects.",
        ]
    )

    write_text_file(output_path, "\n".join(markdown_lines) + "\n")
    info(f"Saved Playwright MCP snapshot to {output_path}")


if __name__ == "__main__":
    try:
        main()
    except McpClientError as caught:
        error(f"Playwright MCP snapshot agent failed: {caught}")
        raise
    except Exception as caught:
        error(f"Unexpected Playwright MCP snapshot failure: {caught}")
        raise
