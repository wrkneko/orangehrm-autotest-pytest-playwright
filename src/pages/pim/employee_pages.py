import random
import re

from playwright.sync_api import Page, expect

from src.pages.base_page import BasePage


class AddEmployeePage(BasePage):
    URL_PATH = "/web/index.php/pim/addEmployee"
    MAX_SAVE_ATTEMPTS = 5

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)
        self.first_name_input = page.locator("input[name='firstName']")
        self.last_name_input = page.locator("input[name='lastName']")
        self.save_button = page.get_by_role("button", name="Save")
        self.employee_id_input = (
            page.locator(".oxd-input-group")
            .filter(has_text="Employee Id")
            .locator("input")
        )
        self.employee_id_taken_error = page.get_by_text(
            "Employee Id already exists")

    def open(self) -> "AddEmployeePage":
        self.goto(self.URL_PATH)
        return self

    def add_employee(self, first_name: str, last_name: str) -> str:
        self.fill(self.first_name_input, first_name, "first name")
        self.fill(self.last_name_input, last_name, "last name")
        self._assign_unique_employee_id()

        for attempt in range(1, self.MAX_SAVE_ATTEMPTS + 1):
            self.click(self.save_button, "Save button")
            try:
                expect(self.page).to_have_url(
                    re.compile(r".*/pim/viewPersonalDetails/empNumber/\d+"),
                    timeout=5000
                )
                break
            except AssertionError:
                if (attempt == self.MAX_SAVE_ATTEMPTS
                        or not self.employee_id_taken_error.is_visible()):
                    raise
                self._assign_unique_employee_id()

        expect(self.page.get_by_role("heading", name="Personal Details")
               ).to_be_visible(timeout=10000)
        expect(self.employee_id_input).to_be_visible(timeout=10000)
        expect(self.employee_id_input).not_to_have_value("", timeout=10000)
        return self.employee_id_input.input_value()

    def _assign_unique_employee_id(self) -> None:
        expect(self.employee_id_input).to_be_visible(timeout=10000)
        new_id = str(random.randint(100000, 999999))
        self.fill(self.employee_id_input, new_id, "employee id")


class EmployeeListPage(BasePage):
    URL_PATH = "/web/index.php/pim/viewEmployeeList"

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)

        self.employee_name_search = (
            page.locator(".oxd-input-group").filter(has_text="Employee Name").locator("input"))
        self.employee_id_search = (page.locator(".oxd-input-group",)
            .filter(has_text="Employee Id")
            .locator("input"))
        self.search_button = page.get_by_role("button", name="Search")
        self.table_rows = page.locator(".oxd-table-card")
        self.no_records_text = page.get_by_text("No Records Found")
        self.delete_selected_button = page.get_by_role("button", name="Delete Selected")
        self.confirm_delete_button = page.get_by_role("button", name="Yes, Delete")
        

    def _select_employee_from_autocomplete(self) -> "EmployeeListPage":
        self.select_from_autocomplete(self.employee_name_search, "Employee name")
        # Wait for autocomplete selection to apply to input
        expect(self.employee_name_search).not_to_have_value("test", timeout=5000)
        return self

    def open(self) -> "EmployeeListPage":
        self.goto(self.URL_PATH)
        return self

    def search_by_id(self, employee_id: str) -> "EmployeeListPage":
        self.fill(self.employee_id_search, employee_id, "employee id search")
        self.click(self.search_button, "Search button")
        self.wait_for_filtered_results(employee_id)
        return self

    def search_by_name(self, name: str) -> "EmployeeListPage":
        self.fill(self.employee_name_search, name, "employee name search")
        self._select_employee_from_autocomplete()
        self.click(self.search_button, "Search button")
        self.wait_for_filtered_results(name)
        # Ensure search results are stable
        self.page.wait_for_load_state("networkidle", timeout=5000)
        return self

    def wait_for_filtered_results(self, expected_text: str, timeout: int = 15000) -> None:
        """
        Waits until the table reflects the applied filter, not just
        'some rows are visible' — old pre-search rows satisfy that
        trivially and cause false positives on fast machines.
        """
        # Wait for table to start loading results
        expect(
            self.table_rows.first.or_(self.no_records_text)
        ).to_be_visible(timeout=timeout)

        # Ensure all visible rows contain the expected text (filter applied)
        expect(
            self.table_rows.filter(has_not_text=expected_text)
        ).to_have_count(0, timeout=timeout)

        # Additional wait for stability, especially after autocomplete
        self.page.wait_for_timeout(1000)

    def get_selected_employee_name(self) -> str:
        return self.employee_name_search.input_value()

    def row_count(self) -> int:
        if self.no_records_text.is_visible():
            return 0
        return self.table_rows.count()

    def has_row_matching(self, text: str) -> bool:
        """
        True if some row contains every whitespace-separated part of
        `text` (in any cell, any order) — e.g. matching "Test 13231"
        against a row where first/last name are in separate cells.
        """
        # Poll for the row to appear, in case of loading delay
        for _ in range(5):
            matches = self.table_rows
            for part in text.split():
                matches = matches.filter(has_text=part)
            if matches.count() > 0:
                return True
            self.page.wait_for_timeout(1000)
        return False

    def delete_first_result(self) -> None:
        row = self.table_rows.first
        expect(row).to_be_visible()
        self.select_row(row, "employee row checkbox")
        expect(self.delete_selected_button).to_be_enabled()
        self.click(self.delete_selected_button, "Delete Selected button")
        self.click(self.confirm_delete_button, "Confirm delete button")
        self.wait_for_toast("Successfully Deleted")

    def employee_exists(self, employee_id: str) -> bool:
        self.search_by_id(employee_id)

        return self.row_count() > 0

    def cleanup_employee(self, employee_id: str) -> None:
        self.open()
        if self.employee_exists(employee_id):
            self.delete_first_result()