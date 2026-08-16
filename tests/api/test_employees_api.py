import pytest



# this test has only the get method because schema is asserted in the
# request method itself, see api_client.py -> get_employees
@pytest.mark.api
@pytest.mark.smoke
def test_get_employees_returns_data(api_client):
    api_client.get_employees()

@pytest.mark.api
@pytest.mark.smoke
def test_create_employee_minimal(tracked_api_client, employee_data):
    employee = tracked_api_client.create_employee(employee_data().to_payload())
    assert employee["lastName"]

@pytest.mark.api
@pytest.mark.regression
def test_create_employee_with_middle_name(tracked_api_client, employee_data):
    employee = tracked_api_client.create_employee(
        employee_data(middle_name="MiddleTest").to_payload()
    )
    assert employee["middleName"] == "MiddleTest"

@pytest.mark.api
@pytest.mark.smoke
def test_create_employee_with_login(tracked_api_client, employee_data, user_data):
    result = tracked_api_client.create_employee_with_login(
        employee_data().to_payload(),
        user_data().to_payload(),
    )
    assert result["user"]["userName"]
