from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.utils.jwt_handler import get_user_id_from_token, get_token_type

security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """
    Извлечение user_id из access JWT токена в заголовке Authorization.
    Проверяет, что токен является access-токеном и действителен.
    
    Args:
        credentials: HTTP Bearer токен
        
    Returns:
        user_id пользователя
        
    Raises:
        HTTPException: если токен невалиден, истёк или имеет неправильный тип
    """
    token = credentials.credentials
    
    token_type = get_token_type(token)
    if token_type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type. Expected access token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = get_user_id_from_token(token)
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_id
