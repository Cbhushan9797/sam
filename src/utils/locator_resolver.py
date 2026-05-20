from __future__ import annotations

from playwright.sync_api import Locator, Page

from src.knowledge.locator_registry import get_registry_locator, get_locator_profile
from src.utils.locator_builder import build_locator
from src.utils.logger import warn


def resolve_locator(page: Page, page_name: str, locator_name: str, fallback: Locator) -> Locator:
    spec = get_registry_locator(page_name, locator_name)
    if not spec:
        return fallback

    try:
        return build_locator(page, spec)
    except Exception as caught:
        warn(
            f"Failed to build locator '{locator_name}' from profile '{get_locator_profile()}' "
            f"for page '{page_name}'. Falling back to in-code locator. Error: {caught}"
        )
        return fallback
