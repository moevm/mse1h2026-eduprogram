from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.utils.jwt_handler import get_user_id_from_token

security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """
    Извлечение user_id из JWT токена в заголовке Authorization.
    Args:
        credentials: HTTP Bearer токен
        
    Returns:
        user_id пользователя
        
    Raises:
        HTTPException: если токен невалиден или истек
    """
    token = credentials.credentials
    user_id = get_user_id_from_token(token)
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_id
