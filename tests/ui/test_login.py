import pytest



@pytest.mark.smoke
@pytest.mark.ui
def test_successful_login(login_page, credentials):
    login_page.login(credentials["username"], credentials["password"])
    login_page.assert_login_successful()


@pytest.mark.regression
@pytest.mark.ui
def test_login_with_invalid_password(login_page, credentials):
    login_page.login(credentials["username"], "wrong-password")
    assert "Invalid credentials" in login_page.get_error_message()


@pytest.mark.regression
@pytest.mark.ui
def test_login_with_empty_credentials(login_page):
    login_page.login("", "")
    login_page.assert_empty_field_required_message()
