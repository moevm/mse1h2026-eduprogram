from test_api.config.base_test import BaseTest

from pytest import mark


@mark.api
class TestDefault(BaseTest):
    def test_registration(self):
        self.api_users.register()
        self.api_users.register_test_user()

    def test_login(self):
        self.api_users.login()