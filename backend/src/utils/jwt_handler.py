import jwt
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
import os


SECRET_KEY = os.getenv("JWT_SECRET_KEY", "test_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15 
REFRESH_TOKEN_EXPIRE_DAYS = 7 


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Создание JWT access-токена для пользователя.
    Короткоживущий токен для доступа к защищённым ресурсам.
    
    Args:
        data: Данные для включения в токен (должна содержать user_id)
        expires_delta: Время истечения токена (если не указано, используется 15 минут)
        
    Returns:
        JWT access-токен в виде строки
    """
    to_encode = data.copy()
    to_encode["token_type"] = "access"
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Создание JWT refresh-токена для пользователя.
    Долгоживущий токен для получения новой пары токенов.
    
    Args:
        data: Данные для включения в токен (должна содержать user_id)
        expires_delta: Время истечения токена (если не указано, используется 7 дней)
        
    Returns:
        JWT refresh-токен в виде строки
    """
    to_encode = data.copy()
    to_encode["token_type"] = "refresh"
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_token_pair(user_id: int) -> Tuple[str, str]:
    """
    Создание пары токенов (access и refresh) для пользователя.
    
    Args:
        user_id: ID пользователя
        
    Returns:
        Кортеж (access_token, refresh_token)
    """
    data = {"user_id": user_id}
    access_token = create_access_token(data)
    refresh_token = create_refresh_token(data)
    return access_token, refresh_token


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Проверка корректности JWT токена (access или refresh).
    
    Args:
        token: JWT токен для проверки
        
    Returns:
        Данные из токена или None если токен невалиден или истёк
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_user_id_from_token(token: str) -> Optional[int]:
    """
    Извлечение user_id из токена.
    
    Args:
        token: JWT токен (access или refresh)
        
    Returns:
        user_id или None если токен невалиден
    """
    payload = verify_token(token)
    if payload and "user_id" in payload:
        return payload["user_id"]
    return None


def get_token_type(token: str) -> Optional[str]:
    """
    Извлечение типа токена (access или refresh).
    
    Args:
        token: JWT токен
        
    Returns:
        Тип токена ('access' или 'refresh') или None если токен невалиден
    """
    payload = verify_token(token)
    if payload and "token_type" in payload:
        return payload["token_type"]
    return None
