from __future__ import annotations


REQUIRED_SNAPSHOT_SECTIONS = (
    "# Playwright MCP Snapshot",
    "## Navigation Result",
    "## Accessibility Snapshot",
)


def is_valid_mcp_snapshot(content: str) -> bool:
    normalized = content.strip()
    if not normalized:
        return False

    if "playwright mcp is disabled" in normalized.lower():
        return False

    return all(section in normalized for section in REQUIRED_SNAPSHOT_SECTIONS)


def require_valid_mcp_snapshot(content: str, source_name: str) -> str:
    if not is_valid_mcp_snapshot(content):
        raise RuntimeError(
            f"{source_name} requires a real Playwright MCP snapshot. "
            "Run `python -m src.agents.mcp_snapshot_agent` successfully before continuing."
        )

    return content
