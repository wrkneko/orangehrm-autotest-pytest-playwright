import pytest



@pytest.mark.smoke
@pytest.mark.ui
def test_page_loads(login_page):
    reset_page = login_page.open_reset_password()
    reset_page.assert_opened()

@pytest.mark.smoke
@pytest.mark.ui
# @pytest.mark.skip
def test_reset_password(login_page, credentials):
    reset_page = login_page.open_reset_password()
    reset_page.reset_password(credentials["username"])
    reset_page.assert_reset_sent()

@pytest.mark.regression
@pytest.mark.ui
def test_reset_password_cancel(login_page, credentials):
    reset_page = login_page.open_reset_password()
    reset_page.cancel().assert_opened()

@pytest.mark.regression
@pytest.mark.ui
def test_username_empty(login_page):
    reset_page = login_page.open_reset_password()
    reset_page.assert_required_username()
