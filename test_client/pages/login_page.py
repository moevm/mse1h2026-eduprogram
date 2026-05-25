from selenium.webdriver.support import expected_conditions as EC

from base.base_page import BasePage
from config.links import Links


class LoginPage(BasePage):
    PAGE_URL = Links.LOGIN

    LOGIN_BUTTON_REDIRECT = ("xpath", "//button[child::span[text()='Вход']]")
    EMAIL_INPUT = ("xpath", "//input[@type='email']")
    PASSWORD_INPUT = ("xpath", "//input[@type='password']")
    LOGIN_BUTTON = ("xpath", "//button[child::span[text()='Войти']]")

    def click_login_redirect(self):
        self.wait.until(EC.element_to_be_clickable(self.LOGIN_BUTTON_REDIRECT)).click()

    def enter_email(self, email: str):
        self.wait.until(EC.element_to_be_clickable(self.EMAIL_INPUT)).send_keys(email)

    def enter_password(self, password: str):
        self.wait.until(EC.element_to_be_clickable(self.PASSWORD_INPUT)).send_keys(password)

    def click_login(self):
        self.wait.until(EC.element_to_be_clickable(self.LOGIN_BUTTON)).click()

    def is_user_logged_in(self):
        self.wait.until(EC.url_to_be(Links.MAIN))
