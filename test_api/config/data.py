from dotenv import load_dotenv

import os

load_dotenv()

class Data:
    host = os.getenv("HOST")
    login = os.getenv("LOGIN")
    password = os.getenv("PASSWORD")
    user_id = os.getenv("USERID")
    access_token = None
    universities = {"ГУАП", "СПБГЭТУ ЛЭТИ", "МПУ", "МТУСИ", "СПБПУ"}