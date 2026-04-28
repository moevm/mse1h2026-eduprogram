from faker import Faker

from test_api.config.data import Data


fake = Faker()

class Payloads:
    test_user_info = {
        "login" : Data.login,
        "password" : Data.password
    }

    random_user_info = {
        "login" : fake.email(),
        "password" : fake.password()
    }