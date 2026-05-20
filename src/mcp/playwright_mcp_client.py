from __future__ import annotations

import json
import os
import shlex
import subprocess
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.utils.file_utils import PROJECT_ROOT


class McpClientError(RuntimeError):
    """Raised when the MCP client cannot complete a request."""


@dataclass
class McpToolCallResult:
    raw: dict[str, Any]
    text_content: str


def _parse_mcp_args(raw_value: str) -> list[str]:
    if not raw_value.strip():
        return ["-y", "@playwright/mcp@latest", "--headless", "--output-dir", "test-results/mcp"]

    try:
        parsed = json.loads(raw_value)
        if isinstance(parsed, list) and all(isinstance(item, str) for item in parsed):
            return parsed
    except json.JSONDecodeError:
        pass

    return shlex.split(raw_value, posix=os.name != "nt")


class PlaywrightMcpClient:
    def __init__(
        self,
        command: str,
        args: list[str],
        *,
        cwd: Path | None = None,
        timeout_seconds: float = 120.0,
    ) -> None:
        self.command = command
        self.args = args
        self.cwd = cwd or PROJECT_ROOT
        self.timeout_seconds = timeout_seconds
        self.process: subprocess.Popen[str] | None = None
        self.next_request_id = 1
        self.stderr_lines: list[str] = []
        self.notifications: list[dict[str, Any]] = []
        self.server_info: dict[str, Any] = {}
        self.server_capabilities: dict[str, Any] = {}
        self.protocol_version = "2024-11-05"
        self._stderr_thread: threading.Thread | None = None

    @classmethod
    def from_env(cls) -> "PlaywrightMcpClient":
        command = os.getenv("PLAYWRIGHT_MCP_COMMAND", "npx").strip() or "npx"
        raw_args = os.getenv("PLAYWRIGHT_MCP_ARGS", "").strip()
        args = _parse_mcp_args(raw_args)
        timeout_seconds = float(os.getenv("PLAYWRIGHT_MCP_TIMEOUT_SECONDS", "120").strip() or "120")
        return cls(command=command, args=args, cwd=PROJECT_ROOT, timeout_seconds=timeout_seconds)

    def __enter__(self) -> "PlaywrightMcpClient":
        self.start()
        return self

    def __exit__(self, exc_type, exc, exc_tb) -> None:
        self.close()

    def start(self) -> None:
        if self.process is not None:
            return

        self.process = subprocess.Popen(
            [self.command, *self.args],
            cwd=self.cwd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
        )
        self._stderr_thread = threading.Thread(target=self._drain_stderr, daemon=True)
        self._stderr_thread.start()

        init_result = self.request(
            "initialize",
            {
                "protocolVersion": self.protocol_version,
                "capabilities": {},
                "clientInfo": {
                    "name": "teamcenter-ai-playwright-python-client",
                    "version": "1.0.0",
                },
            },
        )
        self.server_info = init_result.get("serverInfo", {})
        self.server_capabilities = init_result.get("capabilities", {})
        self.notify("notifications/initialized")

    def close(self) -> None:
        if self.process is None:
            return

        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=5)

        self.process = None

    def request(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        request_id = self.next_request_id
        self.next_request_id += 1
        self._send(
            {
                "jsonrpc": "2.0",
                "id": request_id,
                "method": method,
                "params": params or {},
            }
        )

        deadline = time.monotonic() + self.timeout_seconds
        while True:
            if time.monotonic() > deadline:
                raise McpClientError(f"Timed out waiting for MCP response to {method}.")

            message = self._read_message()
            if message.get("id") == request_id:
                if "error" in message:
                    raise McpClientError(f"MCP error for {method}: {message['error']}")
                return message.get("result", {})

            self._handle_server_message(message)

    def notify(self, method: str, params: dict[str, Any] | None = None) -> None:
        self._send(
            {
                "jsonrpc": "2.0",
                "method": method,
                "params": params or {},
            }
        )

    def list_tools(self) -> list[dict[str, Any]]:
        tools: list[dict[str, Any]] = []
        cursor: str | None = None

        while True:
            result = self.request("tools/list", {"cursor": cursor} if cursor else {})
            tools.extend(result.get("tools", []))
            cursor = result.get("nextCursor")
            if not cursor:
                break

        return tools

    def call_tool(self, name: str, arguments: dict[str, Any] | None = None) -> McpToolCallResult:
        result = self.request(
            "tools/call",
            {
                "name": name,
                "arguments": arguments or {},
            },
        )
        content = result.get("content", [])
        text_chunks: list[str] = []
        for item in content:
            if item.get("type") == "text":
                text_chunks.append(str(item.get("text", "")))
            elif item.get("type") == "resource":
                resource = item.get("resource", {})
                if "text" in resource:
                    text_chunks.append(str(resource.get("text", "")))

        return McpToolCallResult(raw=result, text_content="\n".join(chunk for chunk in text_chunks if chunk).strip())

    def capture_snapshot(self, target_url: str) -> dict[str, Any]:
        tools = self.list_tools()
        tool_names = {tool.get("name", "") for tool in tools}

        missing = [name for name in ("browser_navigate", "browser_snapshot") if name not in tool_names]
        if missing:
            raise McpClientError(
                f"Playwright MCP server is missing required tools: {', '.join(missing)}."
            )

        navigate_result = self.call_tool("browser_navigate", {"url": target_url})
        snapshot_result = self.call_tool("browser_snapshot", {})
        return {
            "tools": tools,
            "navigate": navigate_result,
            "snapshot": snapshot_result,
            "notifications": self.notifications,
            "stderr": self.stderr_lines,
            "serverInfo": self.server_info,
            "serverCapabilities": self.server_capabilities,
        }

    def _send(self, message: dict[str, Any]) -> None:
        if self.process is None or self.process.stdin is None:
            raise McpClientError("MCP process is not running.")

        payload = json.dumps(message, ensure_ascii=False, separators=(",", ":"))
        if "\n" in payload:
            raise McpClientError("MCP stdio messages must not contain embedded newlines.")

        self.process.stdin.write(payload + "\n")
        self.process.stdin.flush()

    def _read_message(self) -> dict[str, Any]:
        if self.process is None or self.process.stdout is None:
            raise McpClientError("MCP process is not running.")

        line = self.process.stdout.readline()
        if not line:
            stderr_tail = "\n".join(self.stderr_lines[-10:])
            raise McpClientError(
                "Playwright MCP server closed unexpectedly."
                + (f"\nRecent stderr:\n{stderr_tail}" if stderr_tail else "")
            )

        try:
            return json.loads(line)
        except json.JSONDecodeError as caught:
            raise McpClientError(f"Received invalid MCP JSON message: {line}") from caught

    def _handle_server_message(self, message: dict[str, Any]) -> None:
        if "method" in message:
            self.notifications.append(message)

    def _drain_stderr(self) -> None:
        if self.process is None or self.process.stderr is None:
            return

        for line in self.process.stderr:
            self.stderr_lines.append(line.rstrip())
