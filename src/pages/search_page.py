from __future__ import annotations

import re

from playwright.sync_api import Locator, Page, expect

from src.utils.locator_resolver import resolve_locator


class SearchPage:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.search_input: Locator = resolve_locator(
            page,
            "search_page",
            "search_input",
            page.get_by_role("searchbox", name=re.compile(r"search", re.I)),
        )
        self.search_button: Locator = resolve_locator(
            page,
            "search_page",
            "search_button",
            page.get_by_role("button", name=re.compile(r"search", re.I)),
        )

    def search_part(self, part_id: str) -> None:
        expect(self.search_input).to_be_visible(timeout=60_000)
        self.search_input.fill(part_id)

        if self.search_button.is_visible():
            self.search_button.click()
        else:
            self.search_input.press("Enter")

    def verify_part_appears_in_results(self, part_id: str) -> None:
        row_match = self.page.get_by_role("row", name=re.compile(re.escape(part_id), re.I)).first
        text_match = self.page.get_by_text(re.compile(re.escape(part_id), re.I)).first

        try:
            expect(row_match).to_be_visible(timeout=60_000)
        except Exception:
            expect(text_match).to_be_visible(timeout=60_000)
