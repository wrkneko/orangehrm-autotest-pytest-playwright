"""
Base Page Object.

All page classes inherit from this to get:
- consistent step-level logging (useful when reading a failed test's log)
- thin wrappers around Playwright actions so a locator change or a new
  cross-cutting behaviour (e.g. custom waits) only needs to change here
- a shared way to assert on the app's toast notifications, which OrangeHRM
  uses for almost every create/update/delete confirmation
"""
import logging

from playwright.sync_api import Page, expect, Locator

logger = logging.getLogger(__name__)


class BasePage:
    CHECKBOX_SELECTOR = ".oxd-checkbox-input"
    
    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url.rstrip("/")

    def goto(self, path: str = "") -> None:
        url = f"{self.base_url}{path}"
        logger.info("Navigating to %s", url)
        self.page.goto(url)

    def click(self, locator, description: str = "") -> None:
        logger.info("Clicking: %s", description or locator)
        locator.click()

    def fill(self, locator, value: str | None = None, description: str = "") -> None:
        logger.info("Filling '%s': %s", description or locator, value)
        locator.fill(value)

    def get_dropdown_options(self, dropdown_locator: Locator) -> list[str]:
        dropdown_locator.click()
        listbox = self.page.get_by_role("listbox").last
        options = listbox.get_by_role("option").all_inner_texts()
        self.page.keyboard.press("Escape")
        return options

    def select_dropdown_option(self, dropdown_locator: Locator,
                               option_text: str) -> None:
        dropdown_locator.click()
        listbox = self.page.get_by_role("listbox").last
        listbox.get_by_role("option", name=option_text, exact=True).click()

    def wait_for_toast(self, expected_text: str | None = None,
                       timeout: int = 5000):
        toast = self.page.locator(".oxd-toast--success")

        expect(toast).to_be_visible(timeout=timeout)

        if expected_text:
            expect(toast).to_contain_text(expected_text, timeout=timeout)

    def row_checkbox(self, row: Locator) -> Locator:
        return row.locator(self.CHECKBOX_SELECTOR)

    def select_row(self, row: Locator,
                   description: str = "row checkbox") -> None:
        self.click(self.row_checkbox(row), description)

