from __future__ import annotations

import re

from playwright.sync_api import Locator, Page, expect

from src.use_cases.part_creation.data_reader import PartData
from src.utils.locator_resolver import resolve_locator


class PartCreationPage:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.create_new_part_button: Locator = resolve_locator(
            page,
            "part_creation_page",
            "create_new_part_button",
            page.get_by_role("button", name=re.compile(r"new part|create new part", re.I)),
        )
        self.part_id_input: Locator = resolve_locator(
            page,
            "part_creation_page",
            "part_id_input",
            page.get_by_label(re.compile(r"part id", re.I)),
        )
        self.part_name_input: Locator = resolve_locator(
            page,
            "part_creation_page",
            "part_name_input",
            page.get_by_label(re.compile(r"part name", re.I)),
        )
        self.part_type_field: Locator = resolve_locator(
            page,
            "part_creation_page",
            "part_type_field",
            page.get_by_label(re.compile(r"part type", re.I)),
        )
        self.description_input: Locator = resolve_locator(
            page,
            "part_creation_page",
            "description_input",
            page.get_by_label(re.compile(r"description", re.I)),
        )
        self.revision_input: Locator = resolve_locator(
            page,
            "part_creation_page",
            "revision_input",
            page.get_by_label(re.compile(r"revision", re.I)),
        )
        self.unit_of_measure_input: Locator = resolve_locator(
            page,
            "part_creation_page",
            "unit_of_measure_input",
            page.get_by_label(re.compile(r"unit of measure|uom", re.I)),
        )
        self.save_button: Locator = resolve_locator(
            page,
            "part_creation_page",
            "save_button",
            page.get_by_role("button", name=re.compile(r"^save$", re.I)),
        )
        self.success_message: Locator = resolve_locator(
            page,
            "part_creation_page",
            "success_message",
            page.get_by_text(re.compile(r"part created successfully|success", re.I)),
        )

    def verify_part_creation_page_loaded(self) -> None:
        try:
            expect(self.part_id_input).to_be_visible(timeout=60_000)
        except Exception:
            expect(self.create_new_part_button).to_be_visible(timeout=60_000)

    def create_part(self, part_data: PartData) -> None:
        self.verify_part_creation_page_loaded()

        if self.create_new_part_button.is_visible():
            self.create_new_part_button.click()

        expect(self.part_id_input).to_be_visible(timeout=60_000)
        self.part_id_input.fill(part_data.partId)
        self.part_name_input.fill(part_data.partName)
        self._fill_combo_or_input(self.part_type_field, part_data.partType)
        self._fill_optional_field(self.description_input, part_data.description)
        self._fill_optional_field(self.revision_input, part_data.revision)
        self._fill_optional_field(self.unit_of_measure_input, part_data.unitOfMeasure)

        # TODO: Add any instance-specific mandatory Teamcenter fields that are not covered by the sample CSV.

    def save_part(self) -> None:
        expect(self.save_button).to_be_visible(timeout=60_000)
        self.save_button.click()

    def verify_part_created(self, part_id: str) -> None:
        try:
            expect(self.success_message).to_be_visible(timeout=60_000)
        except Exception:
            expect(self.page.get_by_text(re.compile(re.escape(part_id), re.I))).to_be_visible(
                timeout=60_000
            )

    def _fill_optional_field(self, locator: Locator, value: str) -> None:
        if not value:
            return

        try:
            locator.wait_for(state="visible", timeout=5_000)
            locator.fill(value)
        except Exception:
            # Optional fields may not exist in every Teamcenter form variation.
            return

    def _fill_combo_or_input(self, locator: Locator, value: str) -> None:
        locator.wait_for(state="visible", timeout=60_000)

        try:
            locator.select_option(label=value)
            return
        except Exception:
            pass

        locator.click()
        locator.fill(value)

        matching_option = self.page.get_by_role("option", name=re.compile(fr"^{re.escape(value)}$", re.I))
        if matching_option.count() > 0:
            matching_option.first.click()
        else:
            locator.press("Enter")
