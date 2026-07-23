import pytest

from src.data.factories import build_employee
from src.pages.pim.employee_pages import AddEmployeePage, EmployeeListPage


@pytest.mark.regression
@pytest.mark.ui
def test_add_and_delete_employee(authenticated_page, base_url):
    employee = build_employee()
    add_page = AddEmployeePage(authenticated_page, base_url).open()
    employee_id = add_page.add_employee(employee.first_name, employee.last_name)
    assert employee_id, "Employee ID should be generated"

    list_page = EmployeeListPage(authenticated_page, base_url)

    try:
        list_page.open()
        list_page.search_by_id(employee_id)
        assert list_page.row_count() == 1
    finally:
        list_page.open()
        list_page.search_by_id(employee_id)
        if list_page.row_count() == 1:
            list_page.delete_first_result()
