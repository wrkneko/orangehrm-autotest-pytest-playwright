from playwright.sync_api import Page, Locator, expect

from src.pages.base_page import BasePage
from src.pages.pim.reports_view_page import ReportsViewPage


class ReportsFormPage(BasePage):
    URL_PATH = "/web/index.php/pim/definePredefinedReport"

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)
        self.report_name_input = page.get_by_placeholder("Type here ...")

        self.selection_criteria_ddl = self._dropdown_by_label("Selection Criteria")
        self.include_ddl = self._dropdown_by_label("Include")
        self.display_field_group_ddl = self._dropdown_by_label("Select Display Field Group")
        self.display_field_ddl = self._dropdown_by_label("Select Display Field")
        self.employee_name_input = (
        self.page.locator(".oxd-form-row").filter(has_text="Employee Name")
            .get_by_placeholder("Type for hints..."))
        self.cancel_btn = page.get_by_role("button", name="Cancel")
        self.save_btn = page.get_by_role("button", name="Save")
        self.add_selection_criteria_btn = self.page.locator(
            ".oxd-form-row",
            has=self.page.get_by_text("Selection Criteria", exact=True)
        ).locator("button.orangehrm-report-icon")

        self.add_display_field_btn = self.page.locator(
            ".oxd-form-row",
            has=self.page.get_by_text("Display Fields", exact=True)
        ).locator("button.orangehrm-report-icon")

    def _dropdown_by_label(self, label_text: str) -> Locator:
        return self.page.locator(
            ".oxd-input-group", has=self.page.get_by_text(label_text, exact=True)
        ).locator(".oxd-select-text-input")

    def _autocomplete_option(self, employee_name: str):
        return self.page.get_by_role(
            "option",
            name=employee_name,
            exact=True
        )

    def open(self) -> "ReportsFormPage":
        self.goto(self.URL_PATH)
        return self

    def expect_form_loaded(self) -> "ReportsFormPage":
        expect(self.report_name_input).to_be_visible()
        return self

    def save(self) -> ReportsViewPage:
        self.click(self.save_btn, "Save report")
        self.wait_for_toast("Successfully Saved")
        view_page = ReportsViewPage(self.page, self.base_url)
        view_page.wait_loaded()
        return view_page

    def cancel(self) -> None:
        self.click(self.cancel_btn, "Cancel report creation")

    def get_selection_criteria_options(self) -> list[str]:
        return self.get_dropdown_options(
            self.selection_criteria_ddl
        )

    def get_include_options(self) -> list[str]:
        return self.get_dropdown_options(
            self.include_ddl
        )

    def get_display_field_group_options(self) -> list[str]:
        return self.get_dropdown_options(
            self.display_field_group_ddl
        )

    def get_display_field_options(self) -> list[str]:
        return self.get_dropdown_options(
            self.display_field_ddl
        )

    def add_selection_criteria(self) -> "ReportsFormPage":
        self.click(self.add_selection_criteria_btn,"Add selection criteria")
        return self

    def add_display_field(self) -> "ReportsFormPage":
        self.click(self.add_display_field_btn, "Add display field")
        return self

    def fill_employee_name(self, employee_name: str) -> "ReportsFormPage":
        self.fill(
            self.employee_name_input,
            employee_name,
            "Employee name"
        )

        self.select_employee_from_autocomplete()

        return self

    def select_employee_from_autocomplete(self) -> "ReportsFormPage":
        self.select_from_autocomplete(self.employee_name_input,
                                      "Employee name")
        return self

    def expect_employee_field_visible(self) -> "ReportsFormPage":
        expect(self.employee_name_input).to_be_visible()
        return self

    def fill_report_name(self, report_name: str) -> "ReportsFormPage":
        self.fill(self.report_name_input, report_name, "Report name")
        return self

    def fill_selection_criteria(self, selection_criteria: str) -> "ReportsFormPage":
        self.select_dropdown_option(self.selection_criteria_ddl, selection_criteria)
        return self

    def fill_include(self, include_ddl_value: str) -> "ReportsFormPage":
        self.select_dropdown_option(self.include_ddl, include_ddl_value)
        return self

    def fill_display_field_group(self, display_field_group_name: str) -> "ReportsFormPage":
        self.select_dropdown_option(self.display_field_group_ddl, display_field_group_name)
        return self

    def fill_display_field(self, display_field_name: str) -> "ReportsFormPage":
        self.select_dropdown_option(self.display_field_ddl, display_field_name)
        return self



