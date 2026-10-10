from playwright.sync_api import Page, expect
from config.settings import BASE_URL


class LoginPage:
    def __init__(self, page: Page):
        self.page = page
        self.username = page.get_by_placeholder("Username")
        self.password = page.get_by_placeholder("Password")
        self.login_button = page.get_by_role(
            "button", name="Login"
        )
        self.error_message = page.locator(
            '[data-test="error"]'
        )

    def open(self):
        self.page.goto(BASE_URL)

    def login(self, username, password):
        self.username.fill(username)
        self.password.fill(password)
        self.login_button.click()

    def verify_login_error(self, message):
        expect(self.error_message).to_contain_text(message)