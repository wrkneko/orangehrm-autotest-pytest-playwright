from __future__ import annotations
import re
from typing import TYPE_CHECKING
from playwright.sync_api import Page, expect
from src.pages.base_page import BasePage

if TYPE_CHECKING:
    from src.pages.reset_password_page import ResetPasswordPage


class LoginPage(BasePage):
    URL_PATH = "/web/index.php/auth/login"

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)
        self.username_input = page.get_by_placeholder("Username")
        self.password_input = page.get_by_placeholder("Password")
        self.submit_button = page.get_by_role("button", name="Login")
        self.error_alert = page.locator(".oxd-alert-content-text")
        self.required_hints = page.get_by_text("Required")
        self.dashboard_header = page.get_by_role("heading", name="Dashboard")
        self.forgot_password_link = page.get_by_text("Forgot your password?",
                                                     exact=True)

    def open(self) -> "LoginPage":
        self.goto(self.URL_PATH)
        return self

    def login(self, username: str, password: str) -> None:
        self.fill(self.username_input, username, "username field")
        self.fill(self.password_input, password, "password field")
        self.click(self.submit_button, "Login button")

    def open_reset_password(self) -> "ResetPasswordPage":
        from src.pages.reset_password_page import ResetPasswordPage  # локальный импорт
        self.click(self.forgot_password_link)
        return ResetPasswordPage(self.page, self.base_url)

    def assert_login_successful(self) -> None:
        expect(self.page).to_have_url(re.compile("dashboard"), timeout = 50000)
        expect(self.dashboard_header).to_be_visible()

    def assert_empty_field_required_message(self) -> None:
        expect(self.required_hints).to_have_count(2)
        expect(self.required_hints.nth(0)).to_be_visible()
        expect(self.required_hints.nth(1)).to_be_visible()

    def get_error_message(self) -> str:
        expect(self.error_alert).to_be_visible(timeout=5000)
        return self.error_alert.inner_text()

    def assert_opened(self):
        expect(self.username_input).to_be_visible(timeout=5000)
        expect(self.password_input).to_be_visible(timeout=5000)
        expect(self.submit_button).to_be_visible(timeout=5000)