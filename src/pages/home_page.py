from __future__ import annotations

import re

from playwright.sync_api import Locator, Page, expect

from src.utils.locator_resolver import resolve_locator


class HomePage:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.part_creation_navigation: Locator = resolve_locator(
            page,
            "home_page",
            "part_creation_navigation",
            page.get_by_text("Part Creation", exact=True),
        )
        self.global_search_input: Locator = resolve_locator(
            page,
            "home_page",
            "global_search_input",
            page.get_by_role("searchbox", name=re.compile(r"search", re.I)),
        )

    def verify_home_page_loaded(self) -> None:
        try:
            expect(self.part_creation_navigation).to_be_visible(timeout=60_000)
        except Exception:
            expect(self.global_search_input).to_be_visible(timeout=60_000)

    def navigate_to_part_creation(self) -> None:
        self.verify_home_page_loaded()
        self.part_creation_navigation.click()
