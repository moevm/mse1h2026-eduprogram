from test_api.services.default.api_default import DefaultAPI
from test_api.config.data import Data


class BaseTest:
    data: Data

    def setup_method(self):
        self.data = Data()
        self.api_users = DefaultAPI()