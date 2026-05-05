from test_api.config.base_test import BaseTest

from pytest import mark


@mark.api
class TestDefault(BaseTest):
    @mark.order(1)
    def test_registration(self):
        response = self.api_users.register()
        assert response.status_code == 201, response.json()

        response = self.api_users.register_test_user()
        assert response.json()

    @mark.order(2)
    def test_login(self):
        response = self.api_users.login()  

        assert response.status_code == 200, response.json().get("id")

    @mark.order(3)
    def test_get_available_universities(self):
        response = self.api_users.get_available_universities()

        assert response.status_code == 200
        assert set(response.json().get("available-universities")) == self.data.universities

    @mark.order(4)
    def test_add_program(self):
        response = self.api_users.add_program()

        assert response.status_code == 200
        assert response.json()

    @mark.order(5)
    @mark.skip(reason="---")
    def test_get_programs(self):
        response = self.api_users.get_programs()

        assert response.status_code == 200
        assert response.json().get("programs")