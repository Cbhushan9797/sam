from __future__ import annotations

import os
import re

from playwright.sync_api import Locator, Page, expect

from src.utils.locator_resolver import resolve_locator


class LoginPage:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.username_input: Locator = resolve_locator(
            page,
            "login_page",
            "username_input",
            page.get_by_label(re.compile(r"user id|username", re.I)),
        )
        self.password_input: Locator = resolve_locator(
            page,
            "login_page",
            "password_input",
            page.get_by_label(re.compile(r"password", re.I)),
        )
        self.sign_in_button: Locator = resolve_locator(
            page,
            "login_page",
            "sign_in_button",
            page.get_by_role("button", name=re.compile(r"sign in|login", re.I)),
        )

    def goto(self) -> None:
        teamcenter_url = os.getenv("TEAMCENTER_URL", "").strip()
        if not teamcenter_url:
            raise RuntimeError("Missing TEAMCENTER_URL. Set it in your .env file before running tests.")

        self.page.goto(teamcenter_url, wait_until="domcontentloaded")

    def is_visible(self) -> bool:
        try:
            return self.username_input.is_visible()
        except Exception:
            return False

    def verify_login_page_loaded(self) -> None:
        expect(self.username_input).to_be_visible(timeout=60_000)
        expect(self.password_input).to_be_visible(timeout=60_000)
        expect(self.sign_in_button).to_be_visible(timeout=60_000)

    def login(self, username: str, password: str) -> None:
        self.verify_login_page_loaded()
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.sign_in_button.click()
