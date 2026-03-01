from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from src.dataBase.dependencies import get_db
from src.dataBase.dataBaseStructs import User
from src.dataBase.dataBaseController import DataBaseController

router = APIRouter()

@router.post("/login")
def login(user: User, db: DataBaseController = Depends(get_db)):
    """Метод обработки входа пользователя.
    Возвращает код и ответ в формате
    {responseMessage: {сообщение от сервера}, id: {id пользователя в БД, если он найден}}"""
    if not db.isConnected():
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"responseMessage": "DataBase connect error!"}
        )
    result = db.findUser(user.login, user.password)
    if "id" not in result:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"responseMessage": "User not found!"}
        )
    return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"responseMessage": "ok", "id": result["id"]}
    )