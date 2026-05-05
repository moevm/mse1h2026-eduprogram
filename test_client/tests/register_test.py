from base.base_test import BaseTest

from pytest import mark


@mark.order(1)
@mark.client
class TestRegister(BaseTest):
    def test_register_test_user(self):

        self.register_page.open()
        self.register_page.is_opened()

        self.register_page.click_register_redirect()
        self.register_page.is_opened()

        self.register_page.enter_email(self.data.LOGIN)
        self.register_page.enter_password(self.data.PASSWORD)
        self.register_page.click_register()

    def test_register(self, user_info):
        email, password = user_info

        self.register_page.open()
        self.register_page.is_opened()

        self.register_page.click_register_redirect()
        self.register_page.is_opened()

        self.register_page.enter_email(email)
        self.register_page.enter_password(password)
        self.register_page.click_register()

        self.register_page.is_user_registered()
        
        