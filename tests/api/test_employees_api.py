import pytest


@pytest.mark.api
@pytest.mark.smoke
@pytest.mark.skip
def test_get_employees_returns_data(api_client):
    result = api_client.get_employees()
    assert "data" in result
    assert isinstance(result["data"], list)
