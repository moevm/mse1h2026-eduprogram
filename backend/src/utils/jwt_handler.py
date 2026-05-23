import jwt
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import os

# SECRET_KEY в .env перенести
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "test_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 часа


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Создание JWT токена для пользователя.
    
    Args:
        data: Данные для включения в токен
        expires_delta: Время истечения токена
        
    Returns:
        JWT токен в виде строки
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Проверка корректности JWT токена.
    
    Args:
        token: JWT токен для проверки
        
    Returns:
        Данные из токена или None если токен невалиден
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
        token: JWT токен
        
    Returns:
        user_id или None если токен невалиден
    """
    payload = verify_token(token)
    if payload and "user_id" in payload:
        return payload["user_id"]
    return None
