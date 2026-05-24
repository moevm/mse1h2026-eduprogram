from typing import Tuple, Dict, Any
from fastapi import status
from src.dataBase.dataBaseController import DataBaseController
from src.dataBase.dataBaseStructs import User
from src.utils.jwt_handler import create_token_pair
import hashlib
from datetime import datetime, timedelta


class AuthService:
    """Сервис для аутентификации и регистрации пользователей."""

    def __init__(self, db: DataBaseController):
        self.db = db

    @staticmethod
    def _hash_token(token: str) -> str:
        """
        Хеширование токена для безопасного хранения в БД.
        """
        return hashlib.sha256(token.encode()).hexdigest()

    def login_user(self, user: User) -> Tuple[int, Dict[str, Any]]:
        """
        Обработка входа пользователя.
        Возвращает код и ответ в формате:
        {
            responseMessage: сообщение от сервера,
            access_token: JWT access-токен (15 минут),
            refresh_token: JWT refresh-токен (7 дней),
            id: id пользователя в БД
        }
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

        user_id = result["id"]
        access_token, refresh_token = create_token_pair(user_id)
        
        token_hash = self._hash_token(refresh_token)
        expires_at = datetime.utcnow() + timedelta(days=7)
        
        if not self.db.add_refresh_token(user_id, token_hash, expires_at):
            return (
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                {"responseMessage": "Failed to save refresh token"}
            )

        return (
            status.HTTP_200_OK,
            {
                "responseMessage": "ok",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "id": user_id
            }
        )

    def register_user(self, user: User) -> Tuple[int, Dict[str, Any]]:
        """
        Обработка регистрации пользователя.
        Возвращает код и ответ в формате:
        {
            responseMessage: сообщение от сервера,
            access_token: JWT access-токен (15 минут),
            refresh_token: JWT refresh-токен (7 дней),
            id: id пользователя в БД
        }
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
            user_id = find_result["id"]
            access_token, refresh_token = create_token_pair(user_id)
            
            token_hash = self._hash_token(refresh_token)
            expires_at = datetime.utcnow() + timedelta(days=7)
            
            if not self.db.add_refresh_token(user_id, token_hash, expires_at):
                return (
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    {"responseMessage": "Failed to save refresh token"}
                )
            
            return (
                status.HTTP_201_CREATED,
                {
                    "responseMessage": "User was successfully registered!",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "id": user_id
                }
            )

        return (
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            {"responseMessage": "Cannot register user due to server error!"}
        )