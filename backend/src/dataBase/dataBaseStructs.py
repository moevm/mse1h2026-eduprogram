from pydantic import BaseModel

class User(BaseModel):
    """Структура, которую должна получать серверная часть от клиентской"""
    login: str
    password: str