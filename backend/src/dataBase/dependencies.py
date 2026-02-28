from .dataBaseController import DataBaseController
import os
from dotenv import load_dotenv

load_dotenv()

_db_instance = None


def get_db():
    """Метод создания объект контроллера БД для дальнейшего открытия соединения и создания запросов"""
    global _db_instance
    if _db_instance is None:
        _db_instance = DataBaseController(os.getenv('DB_NAME'), os.getenv('DB_HOST'), os.getenv('DB_PORT'),
                                          os.getenv('DB_USER'), os.getenv('DB_PASSWORD'),
                                          int(os.getenv('DB_MIN_CONN_NUMBER')),
                                          int(os.getenv('DB_MAX_CONN_NUMBER')))
    return _db_instance
