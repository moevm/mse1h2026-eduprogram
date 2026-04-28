from test_api.services.default.api_default import DefaultAPI

class BaseTest:

    def setup_method(self):
        self.api_users = DefaultAPI()