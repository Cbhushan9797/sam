from __future__ import annotations

import re
from typing import Any

from playwright.sync_api import Locator, Page


def build_locator(page: Page, spec: dict[str, Any]) -> Locator:
    strategy = str(spec.get("strategy", "")).strip()
    value = spec.get("value")

    if not strategy or value is None:
        raise ValueError(f"Invalid locator spec: {spec}")

    options = spec.get("options", {})
    exact = bool(options.get("exact", False))
    flags = re.I if "IGNORECASE" in spec.get("flags", []) else 0
    pattern = re.compile(str(value), flags)

    if strategy == "label":
        return page.get_by_label(str(value), exact=exact)
    if strategy == "label_regex":
        return page.get_by_label(pattern)
    if strategy == "role":
        return page.get_by_role(str(options.get("role", "")), name=str(value), exact=exact)
    if strategy == "role_regex":
        return page.get_by_role(str(options.get("role", "")), name=pattern)
    if strategy == "text":
        return page.get_by_text(str(value), exact=exact)
    if strategy == "text_regex":
        return page.get_by_text(pattern)
    if strategy == "searchbox":
        return page.get_by_role("searchbox", name=pattern if not exact else str(value))
    if strategy == "test_id":
        return page.get_by_test_id(str(value))
    if strategy == "css":
        return page.locator(str(value))
    if strategy == "placeholder":
        return page.get_by_placeholder(str(value), exact=exact)

    raise ValueError(f"Unsupported locator strategy: {strategy}")
