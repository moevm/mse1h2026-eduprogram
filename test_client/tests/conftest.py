from pytest import fixture

from pages.login_page import LoginPage

from dotenv import load_dotenv

import os


load_dotenv()

@fixture(scope="function")
def login_user(driver):
    login_page = LoginPage(driver)

    login_page.open()

    login_page.enter_email(os.getenv("LOGIN"))
    login_page.enter_password(os.getenv("PASSWORD"))
    login_page.click_login()