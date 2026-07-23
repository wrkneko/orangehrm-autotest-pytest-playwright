from playwright.sync_api import Page, expect

from src.pages.base_page import BasePage


class ReportsViewPage(BasePage):

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)
        self.main_title = self.page.locator(".orangehrm-main-title")




    def get_report_name(self) -> str:
        return self.main_title.inner_text()

    def wait_loaded(self):
        expect(
            self.main_title,
        ).to_be_visible()