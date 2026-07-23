import pytest

from src.data.factories import build_employee
from src.pages.pim.employee_pages import AddEmployeePage, EmployeeListPage


@pytest.mark.regression
@pytest.mark.ui
def test_add_and_delete_employee(authenticated_page, base_url, employee_cleanup):
    employee = build_employee()
    add_page = AddEmployeePage(authenticated_page, base_url).open()
    employee_id = add_page.add_employee(employee.first_name, employee.last_name)
    assert employee_id, "Employee ID should be generated"
    employee_cleanup(employee_id)

    list_page = EmployeeListPage(authenticated_page, base_url)
    list_page.open()
    list_page.search_by_id(employee_id)
    assert list_page.row_count() == 1

    list_page.delete_first_result()

@pytest.mark.regression
@pytest.mark.ui
def test_search_by_employee_name_filters_results(authenticated_page, base_url):
    list_page = EmployeeListPage(authenticated_page, base_url).open()
    list_page.search_by_name("test")

    selected_name = list_page.get_selected_employee_name()
    assert list_page.has_row_matching(selected_name), \
        f"Expected filtered table to contain a row matching selected employee '{selected_name}'"




