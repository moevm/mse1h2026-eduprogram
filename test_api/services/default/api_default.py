from test_api.config.headers import Headers
from test_api.services.default.endopints import Endpoints
from test_api.services.default.payloads import Payloads

from test_api.config.data import Data

import json

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
        Data.user_id = response.json().get("id")
        return response

    def register_test_user(self):
        response = requests.post(
            url=self.endopints.registration,
            json=self.payloads.test_user_info
        )
        return response

    def login(self):
        response = requests.post(
            url=self.endopints.login,
            json=self.payloads.test_user_info
        )
        return response
    
    def add_program(self):
        self.payloads.program_info["idUser"] = Data.user_id

        response = requests.post(
            url=self.endopints.add_program,
            json=self.payloads.program_info
        )
        return response

    def get_available_universities(self):
        response = requests.get(
            url=self.endopints.get_available_universities
        )

        return response

    def get_programs(self):
        response = requests.get(
            url=self.endopints.get_programs,
            headers = {"userId" : str(Data.user_id)}
        )
        return response