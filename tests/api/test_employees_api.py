import pytest


@pytest.mark.api
@pytest.mark.smoke
@pytest.mark.skip
def test_get_employees_returns_data(api_client):
    result = api_client.get_employees()
    assert "data" in result
    assert isinstance(result["data"], list)

def test_create_employee_minimal(tracked_api_client, employee_data):
    employee = tracked_api_client.create_employee(employee_data().to_payload())
    assert employee["lastName"]


def test_create_employee_with_middle_name(tracked_api_client, employee_data):
    employee = tracked_api_client.create_employee(
        employee_data(middle_name="MiddleTest").to_payload()
    )
    assert employee["middleName"] == "MiddleTest"


def test_create_employee_with_login(tracked_api_client, employee_data, user_data):
    result = tracked_api_client.create_employee_with_login(
        employee_data().to_payload(),
        user_data().to_payload(),
    )
    assert result["user"]["userName"]