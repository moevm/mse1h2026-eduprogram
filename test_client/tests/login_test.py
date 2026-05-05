from base.base_test import BaseTest

from pytest import mark


@mark.order(2)
@mark.client
class TestLogin(BaseTest):
    def test_login(self):
        self.login_page.open()
        self.login_page.is_opened()

        self.login_page.click_login_redirect()
        self.login_page.is_opened()

        self.login_page.enter_email(self.data.LOGIN)
        self.login_page.enter_password(self.data.PASSWORD)
        self.login_page.click_login()

        self.login_page.is_user_logged_in()
        
        