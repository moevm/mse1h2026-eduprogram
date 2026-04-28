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

    program_info = {
        "program_name": [
        {
            "discipline1": {
            "previousDisciplines": [
                "prev_discipline1",
                "prev_discipline2"
            ],
            "topics": []
            }
        },
        {
            "discipline2": {
            "previousDisciplines": [
                "prev_discipline22",
                "prev_discipline21"
            ],
            "topics": []
            }
        },
        {
            "discipline3": {
            "previousDisciplines": [
                "prev_discipline31",
                "prev_discipline32"
            ],
            "topics": []
            }
        }
        ]
    }