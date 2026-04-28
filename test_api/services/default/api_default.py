from test_api.config.headers import Headers
from test_api.services.default.endopints import Endpoints
from test_api.services.default.payloads import Payloads

import requests


class DefaultAPI:
    def __init__(self):
        self.headers = Headers()
        self.endopints = Endpoints()
        self.payloads = Payloads()
        self.user_id = 0

    def register(self):
        response = requests.post(
            url=self.endopints.registration,
            json=self.payloads.random_user_info
        )
        assert response.status_code == 201, response.json()

    def register_test_user(self):
        response = requests.post(
            url=self.endopints.registration,
            json=self.payloads.test_user_info
        )
        assert response.json()
        self.user_id = response.json().get("id")

    def login(self):
        response = requests.post(
            url=self.endopints.login,
            json=self.payloads.test_user_info
        )
        assert response.status_code == 200, response.json().get("id")

    