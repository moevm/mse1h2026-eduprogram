from typing import Tuple, Dict, Any
from fastapi import status
from src.dataBase.dataBaseController import DataBaseController
from src.dataBase.dataBaseStructs import User


class AuthService:
    """Сервис для аутентификации и регистрации пользователей."""

    def __init__(self, db: DataBaseController):
        self.db = db

    def login_user(self, user: User) -> Tuple[int, Dict[str, Any]]:
        """Обработка входа пользователя.
        Возвращает код и ответ в формате:
        {responseMessage: {сообщение от сервера}, id: {id пользователя в БД, если он найден}}
        """
        if not self.db.isConnected():
            return (
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                {"responseMessage": "DataBase connect error!"}
            )

        result = self.db.findUserByLoginPassword(user.login, user.password)
        if "id" not in result:
            return (
                status.HTTP_401_UNAUTHORIZED,
                {"responseMessage": "User not found!"}
            )

        return (
            status.HTTP_200_OK,
            {"responseMessage": "ok", "id": result["id"]}
        )

    def register_user(self, user: User) -> Tuple[int, Dict[str, Any]]:
        """Обработка регистрации пользователя.
        Возвращает код и ответ в формате:
        {responseMessage: {сообщение от сервера}, id: {id пользователя в БД, если он найден}}
        """
        if not self.db.isConnected():
            return (
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                {"responseMessage": "DataBase connect error!"}
            )

        find_result = self.db.findUserByLogin(user.login)

        if "id" in find_result:
            return (
                status.HTTP_409_CONFLICT,
                {"responseMessage": "This login is already in use!"}
            )

        add_result = self.db.addUser(user.login, user.password)

        if add_result:
            find_result = self.db.findUserByLogin(user.login)
            return (
                status.HTTP_201_CREATED,
                {"responseMessage": "User was successfully registered!", "id": find_result["id"]}
            )

        return (
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            {"responseMessage": "Cannot register user due to server error!"}
        )