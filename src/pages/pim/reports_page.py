from playwright.sync_api import Page, expect

from src.pages.base_page import BasePage
from src.pages.pim.reports_form_page import ReportsFormPage
from src.pages.pim.reports_view_page import ReportsViewPage


class ReportsPage(BasePage):
    URL_PATH = "/web/index.php/pim/viewDefinedPredefinedReports"
    CHECKBOX_SELECTOR = "i.oxd-icon.bi-check"

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)
        self.report_name_input = page.get_by_placeholder("Type for hints...")
        self.reset_btn = page.get_by_role("button", name="Reset")
        self.search_btn = page.get_by_role("button", name="Search")
        self.add_btn = page.get_by_role("button", name="Add")
        self.records_found_text = page.locator("text=Records Found")
        self.table_rows = page.locator(".oxd-table-card")
        self.delete_selected_btn = page.get_by_role("button", name="Delete Selected")
        self.delete_modal_confirm = page.get_by_role("button", name="Yes, Delete")
        self.delete_modal_cancel = page.get_by_role("button", name="No, Cancel")
        self.autocomplete_dropdown = page.get_by_role("listbox")

    def _row(self, report_name: str):
        return self.table_rows.filter(has_text=report_name)

    def _trash_btn(self, report_name: str):
        return self._row(report_name).locator("i.bi-trash")

    def _edit_btn(self, report_name: str):
        return self._row(report_name).locator("i.bi-pencil-fill")

    def _view_btn(self, report_name: str):
        return self._row(report_name).locator(".bi-file-text-fill")

    def _autocomplete_option(self, report_name: str):
        return self.page.get_by_role("option", name=report_name, exact=True)

    def _report_name_cell(self, report_name: str):
        return self._row(report_name).get_by_role("cell").nth(1)

    def open(self) -> "ReportsPage":
        self.goto(self.URL_PATH)
        return self

    def search_report(self, report_name: str) -> "ReportsPage":
        self.report_name_input.fill(report_name)
        self.click(self._autocomplete_option(report_name))
        self.click(self.search_btn)
        return self

    def get_autocomplete_suggestions(self, timeout: int = 15000) -> list[str]:
        options = self.autocomplete_dropdown.get_by_role("option")
        expect(options.first).to_be_visible(timeout=timeout)
        expect(self.autocomplete_dropdown.get_by_text(
            "Searching....")).to_be_hidden(timeout=timeout)
        return options.all_text_contents()

    def reset_report(self) -> "ReportsPage":
        self.click(self.reset_btn)
        return self

    def select_report(self, report_name: str) -> "ReportsPage":
        self.select_row(self._row(report_name), f"Select report: {report_name}")
        return self

    def open_add_report(self) -> ReportsFormPage:
        self.click(self.add_btn)
        return ReportsFormPage(self.page, self.base_url)

    def open_edit_report(self, report_name: str) -> ReportsFormPage:
        self.click(self._edit_btn(report_name))
        return ReportsFormPage(self.page, self.base_url)

    def open_view_report(self, report_name: str) -> ReportsViewPage:
        self.click(self._view_btn(report_name))
        return ReportsViewPage(self.page, self.base_url)

    def delete_report(self, report_name: str) -> "ReportsPage":
        self.select_report(report_name)
        self.delete_selected_report()
        self.accept_delete_modal()
        return self

    def delete_selected_report(self):
        self.click(self.delete_selected_btn)

    def accept_delete_modal(self):
        self.click(self.delete_modal_confirm)

    def cancel_delete_modal(self):
        self.click(self.delete_modal_cancel)

    def get_records_count(self):
        text = self.records_found_text.inner_text()
        return int(text.lstrip("(").split(")")[0])

    def check_report_present(self, report_name: str) -> bool:
        expect(
            self._row(report_name)
        ).to_have_count(1)

        return True

    def expect_report_absent(self, report_name: str,
                             timeout: int = 5000) -> None:
        expect(
            self._row(report_name)
        ).to_have_count(0, timeout=timeout)

    def wait_deleted_report_disappears(
            self,
            report_name: str,
            timeout: int = 5000
    ):
        expect(
            self._row(report_name)
        ).to_have_count(0, timeout=timeout)
