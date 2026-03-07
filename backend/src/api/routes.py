from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from src.dataBase.dependencies import get_db
from src.dataBase.dataBaseStructs import User, WorkProgram
from src.dataBase.dataBaseController import DataBaseController
import os
from pathlib import Path
import json

router = APIRouter()

def uploadFileWorkProgram(pathWorkProgram: Path, workProgram: WorkProgram) -> tuple[bool, bool]:
    """Метод загрузки файла учебной и создания папок с университетом и направлением"""
    isExistDirectionPath = False
    isExistWorkProgramPath = False
    if pathWorkProgram.parent.exists():
        isExistDirectionPath = True
    pathWorkProgram.parent.mkdir(parents=True, exist_ok=True)
    topicsDirection = {}
    for topic in workProgram.topics:
        topicsDirection[topic] = workProgram.topics[topic].educationalUnits
    programWorkDictionary = {
        "name": workProgram.nameWorkProgram,
        "previousDisciplines": workProgram.previousDisciplines,
        "topics": topicsDirection
    }
    if pathWorkProgram.exists():
        isExistWorkProgramPath = True
    with open(pathWorkProgram, 'w', encoding="utf-8") as fileWorkProgramJson:
        json.dump(programWorkDictionary, fileWorkProgramJson, indent=4, ensure_ascii=False)

    return isExistDirectionPath, isExistWorkProgramPath

@router.post("/login")
def login(user: User, db: DataBaseController = Depends(get_db)):
    """Метод обработки входа пользователя.
    Возвращает код и ответ в формате.
    {responseMessage: {сообщение от сервера}, id: {id пользователя в БД, если он найден}}"""
    if not db.isConnected():
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"responseMessage": "DataBase connect error!"}
        )
    result = db.findUserByLoginPassword(user.login, user.password)
    if "id" not in result:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"responseMessage": "User not found!"}
        )
    return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"responseMessage": "ok", "id": result["id"]}
    )

@router.post("/add-program")
def addProgram(workProgram: WorkProgram, db: DataBaseController = Depends(get_db)):
    """Метод добавления учебной программы.
    Возвращает код и ответ в формате.
    {responseMessage: {сообщение от сервера}}"""
    if not db.isConnected():
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"responseMessage": "DataBase connect error!"}
        )
    user = db.findUserById(workProgram.idUser)
    if len(user) == 0:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"responseMessage": "Not find current user!"}
        )
    pathStorage = Path(os.getenv('LOCAL_PATH_TO_STORAGE'))
    pathWorkProgram = (Path(workProgram.nameUniversity) / workProgram.nameDirection /
                       f"{workProgram.nameWorkProgram}_{workProgram.idUser}.json")
    isExistDirectionPath, isExistWorkProgramPath = uploadFileWorkProgram(pathStorage / pathWorkProgram, workProgram)
    if not isExistDirectionPath:
        addResult = db.addUserFolder(workProgram.idUser, str(pathWorkProgram.parent))
        if not addResult:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"responseMessage": "DataBase add user folder error!"}
            )
    if not isExistWorkProgramPath:
        addResult = db.addWorkProgram(workProgram.idUser, str(pathWorkProgram.parent), str(pathWorkProgram))
        if not addResult:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"responseMessage": "DataBase add user file error!"}
            )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"responseMessage": "ok"}
    )
