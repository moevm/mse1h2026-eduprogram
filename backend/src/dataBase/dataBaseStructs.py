from pydantic import BaseModel
from typing import List, Dict

class User(BaseModel):
    """Структура для POST:/login, которую должна получать серверная часть от клиентской
    {
        login: str,
        password: str
    }"""
    login: str
    password: str

class Topic(BaseModel):
    """Структура тем в учебной программе"""
    educationalUnits: List[str]

class WorkProgram(BaseModel):
    """Структура POST:/add-program, которую должна получать серверная часть от клиентской
        {
            idUser: int
            nameUniversity: str,
            nameDirection: str,
            nameWorkProgram: str,
            previousDisciplines: list[str],
            topics: {
                str: []
            }
        }
    """
    idUser: int
    nameUniversity: str
    nameDirection: str
    nameWorkProgram: str
    previousDisciplines: List[str]
    topics: Dict[str, Topic]
