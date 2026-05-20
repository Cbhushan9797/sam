from __future__ import annotations

import os
from typing import Any

import requests


def chat_with_ollama(messages: list[dict[str, str]]) -> str:
    base_url = os.getenv("OLLAMA_BASE_URL", "").strip()
    if not base_url:
        raise RuntimeError("Missing OLLAMA_BASE_URL. Set it in your .env file before running the agents.")

    model = os.getenv("OLLAMA_MODEL", "").strip()
    if not model:
        raise RuntimeError("Missing OLLAMA_MODEL. Set it in your .env file before running the agents.")

    endpoint = f"{base_url.rstrip('/')}/api/chat"

    try:
        response = requests.post(
            endpoint,
            json={
                "model": model,
                "stream": False,
                "messages": messages,
            },
            timeout=180,
        )
    except requests.RequestException as caught:
        raise RuntimeError(f"Failed to reach hosted Ollama endpoint {endpoint}: {caught}") from caught

    if not response.ok:
        raise RuntimeError(
            f"Ollama request failed with {response.status_code} {response.reason}. "
            f"Response: {response.text or 'No response body'}"
        )

    try:
        payload: dict[str, Any] = response.json()
    except ValueError as caught:
        raise RuntimeError("Ollama returned a non-JSON response.") from caught

    content = str(payload.get("message", {}).get("content", "")).strip()
    if not content:
        raise RuntimeError("Ollama returned an empty model response.")

    return content
