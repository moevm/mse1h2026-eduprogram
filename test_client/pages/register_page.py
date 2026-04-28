from selenium.webdriver.support import expected_conditions as EC

from base.base_page import BasePage
from config.links import Links


class RegisterPage(BasePage):
    PAGE_URL = Links.REGISTER

    REGISTER_BUTTON_REDIRECT = ("xpath", "//button[child::span[text()='Регистрация']]")
    EMAIL_INPUT = ("xpath", "//input[@type='email']")
    PASSWORD_INPUT = ("xpath", "//input[@type='password']")
    REGISTER_BUTTON = ("xpath", "//button[child::span[text()='Зарегистрироваться']]")

    def click_register_redirect(self):
        REGISTER_BUTTON_REDIRECT_EL = self.wait.until(EC.element_to_be_clickable(self.REGISTER_BUTTON_REDIRECT))
        REGISTER_BUTTON_REDIRECT_EL.click()

    def enter_email(self, email: str):
        EMAIL_INPUT_EL = self.wait.until(EC.element_to_be_clickable(self.EMAIL_INPUT))
        EMAIL_INPUT_EL.send_keys(email)

    def enter_password(self, password: str):
        PASSWORD_INPUT_EL = self.wait.until(EC.element_to_be_clickable(self.PASSWORD_INPUT))
        PASSWORD_INPUT_EL.send_keys(password)

    def click_register(self):
        LOGIN_BUTTON_EL = self.wait.until(EC.element_to_be_clickable(self.REGISTER_BUTTON))
        LOGIN_BUTTON_EL.click()

    def is_user_registered(self):
        self.wait.until(EC.url_to_be(Links.MAIN))
