from fastapi import APIRouter, Body, Depends, status, UploadFile, File, Form
from fastapi.responses import JSONResponse
from src.dataBase.dependencies import get_db
from src.rdf.dependencies import get_rdf
from src.dataBase.dataBaseStructs import User
from src.dataBase.dataBaseController import DataBaseController
from src.rdf.rdf_controller import RdfController
from src.services.auth_service import AuthService
from src.services.program_service import ProgramService
from src.services.graph_service import GraphService
from typing import Any

router = APIRouter()


@router.post("/login")
def login(user: User, db: DataBaseController = Depends(get_db)):
    """Метод обработки входа пользователя."""
    auth_service = AuthService(db)
    status_code, content = auth_service.login_user(user)
    return JSONResponse(status_code=status_code, content=content)


@router.post("/registration")
def registration(user: User, db: DataBaseController = Depends(get_db)):
    """Метод обработки регистрации пользователя."""
    auth_service = AuthService(db)
    status_code, content = auth_service.register_user(user)
    return JSONResponse(status_code=status_code, content=content)


@router.post("/add-program")
def addProgram(payload: Any = Body(...), db: DataBaseController = Depends(get_db),
               rdf: RdfController = Depends(get_rdf)):
    """Метод добавления учебной программы."""
    program_service = ProgramService(db, rdf)
    status_code, content = program_service.add_program(payload)
    return JSONResponse(status_code=status_code, content=content)


@router.get("/get-programs")
def getPrograms(userId: int, db: DataBaseController = Depends(get_db)):
    """Метод получения списка программ пользователя."""
    program_service = ProgramService(db)
    status_code, content = program_service.get_programs(userId)
    return JSONResponse(status_code=status_code, content=content)


@router.get("/show-graph")
def getCertainProgram(userId: int, pathToProgramFolder: str, db: DataBaseController = Depends(get_db)):
    """Метод получения графа учебной программы."""
    graph_service = GraphService(db)
    status_code, content = graph_service.get_certain_program(userId, pathToProgramFolder)
    return JSONResponse(status_code=status_code, content=content)


@router.get("/get-available-universities")
def getAvailableUniversities(db: DataBaseController = Depends(get_db)):
    """Метод получения списка доступных университетов."""
    program_service = ProgramService(db)
    status_code, content = program_service.get_available_universities()
    return JSONResponse(status_code=status_code, content=content)


@router.post("/add-program-from-files")
async def add_program_from_files(
    files: list[UploadFile] = File(...),
    university_name: str = Form(...),
    id_user: int = Form(...),
    db: DataBaseController = Depends(get_db),
    rdf: RdfController = Depends(get_rdf)
):
    """Метод добавления учебной программы из файлов."""
    program_service = ProgramService(db, rdf)
    status_code, content = await program_service.add_program_from_files(files, university_name, id_user)
    return JSONResponse(status_code=status_code, content=content)