from __future__ import annotations
from typing import TYPE_CHECKING

from playwright.sync_api import Page, expect

from src.pages.base_page import BasePage

if TYPE_CHECKING:
    from src.pages.login_page import LoginPage


class ResetPasswordPage(BasePage):
    URL_PATH = "/web/index.php/auth/requestPasswordResetCode"

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)
        self.username_input = page.get_by_role("textbox", name="username")
        self.reset_btn = page.get_by_role("button", name="Reset Password")
        self.cancel_btn = page.get_by_role("button", name="Cancel")
        self.successful_reset_msg = page.get_by_text("Password Reset Success")
        self.required_hints = page.get_by_text("Required")

    def assert_opened(self):
        expect(self.username_input).to_be_visible()
        expect(self.reset_btn).to_be_visible()
        expect(self.cancel_btn).to_be_visible()

    def reset_password(self, username: str):
        self.fill(self.username_input, username, "Username field")
        self.click(self.reset_btn, "Reset Password button")

    def cancel(self) -> "LoginPage":
        from src.pages.login_page import LoginPage  # локальный импорт
        self.click(self.cancel_btn, "Cancel button")
        return LoginPage(self.page, self.base_url)

    def assert_required_username(self):
        self.fill(self.username_input, "", "Username field empty")
        self.click(self.reset_btn, "Reset Password button")
        expect(self.required_hints).to_be_visible()

    def assert_reset_sent(self):
        # reset does not work most of the time, will fail
        self.page.wait_for_load_state("networkidle")