from fastapi import APIRouter, Body, Depends, status, UploadFile, File, Form
from fastapi.responses import JSONResponse
from src.dataBase.dependencies import get_db
from src.rdf.dependencies import get_rdf
from src.api.dependencies import get_current_user
from src.dataBase.dataBaseStructs import User
from src.dataBase.dataBaseController import DataBaseController
from src.rdf.rdf_controller import RdfController
from src.services.auth_service import AuthService
from src.services.program_service import ProgramService
from src.services.graph_service import GraphService
from src.services.gigachat_service import GigachatService
from src.dataBase.dataBaseStructs import ProgramReference
from src.utils.jwt_handler import verify_token, get_user_id_from_token, create_token_pair, get_token_type
from typing import List
from typing import Any
import hashlib
from datetime import datetime, timedelta

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


@router.post("/refresh-tokens")
def refresh_tokens(payload: Any = Body(...), db: DataBaseController = Depends(get_db)):
    """
    Эндпоинт для получения новой пары токенов (access + refresh).
    
    Требует в теле запроса:
    {
        "refresh_token": "старый refresh-токен"
    }
    
    Возвращает:
    {
        "responseMessage": "ok",
        "access_token": "новый access-токен",
        "refresh_token": "новый refresh-токен"
    }
    """
    if not db.isConnected():
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"responseMessage": "Database connection error"}
        )
    
    if not isinstance(payload, dict) or "refresh_token" not in payload:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"responseMessage": "refresh_token is required"}
        )
    
    refresh_token = payload.get("refresh_token")
    
    token_type = get_token_type(refresh_token)
    if token_type != "refresh":
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"responseMessage": "Invalid token type. Expected refresh token."}
        )
    
    user_id = get_user_id_from_token(refresh_token)
    if user_id is None:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"responseMessage": "Invalid or expired refresh token"}
        )
    
    token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
    if not db.is_refresh_token_valid(user_id, token_hash):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"responseMessage": "Refresh token has been revoked or expired"}
        )
    
    new_access_token, new_refresh_token = create_token_pair(user_id)
    
    new_token_hash = hashlib.sha256(new_refresh_token.encode()).hexdigest()
    expires_at = datetime.utcnow() + timedelta(days=7)
    
    if not db.add_refresh_token(user_id, new_token_hash, expires_at):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"responseMessage": "Failed to save refresh token"}
        )
    
    db.revoke_refresh_token(token_hash)
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "responseMessage": "ok",
            "access_token": new_access_token,
            "refresh_token": new_refresh_token
        }
    )


@router.post("/logout")
def logout(payload: Any = Body(...), db: DataBaseController = Depends(get_db)):
    """
    Эндпоинт для выхода (отзыва refresh-токена).
    
    Требует в теле запроса:
    {
        "refresh_token": "токен, который нужно отозвать"
    }
    """
    if not db.isConnected():
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"responseMessage": "Database connection error"}
        )
    
    if not isinstance(payload, dict) or "refresh_token" not in payload:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"responseMessage": "refresh_token is required"}
        )
    
    refresh_token = payload.get("refresh_token")
    
    token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
    db.revoke_refresh_token(token_hash)
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"responseMessage": "Logged out successfully"}
    )


@router.post("/add-program")
def addProgram(payload: Any = Body(...), user_id: int = Depends(get_current_user),
               db: DataBaseController = Depends(get_db),
               rdf: RdfController = Depends(get_rdf)):
    """Метод добавления учебной программы."""
    program_service = ProgramService(db, rdf)
    # установка user_id из токена
    if isinstance(payload, dict):
        payload["idUser"] = user_id
    status_code, content = program_service.add_program(payload)
    return JSONResponse(status_code=status_code, content=content)


@router.get("/get-programs")
def getPrograms(user_id: int = Depends(get_current_user), db: DataBaseController = Depends(get_db), 
                rdf: RdfController = Depends(get_rdf)):
    """Метод получения списка программ пользователя."""
    program_service = ProgramService(db, rdf)
    status_code, content = program_service.get_programs(user_id)
    return JSONResponse(status_code=status_code, content=content)


@router.get("/show-graph")
def getCertainProgram(user_id: int = Depends(get_current_user), pathToProgramFolder: str = None, 
                      universityName: str | None = None,
                      db: DataBaseController = Depends(get_db),
                      rdf: RdfController = Depends(get_rdf)):
    """Метод получения графа учебной программы."""
    graph_service = GraphService(db, None, rdf)
    status_code, content = graph_service.get_certain_program(user_id, pathToProgramFolder, universityName)
    return JSONResponse(status_code=status_code, content=content)


@router.get("/get-available-universities")
def getAvailableUniversities(db: DataBaseController = Depends(get_db)):
    """Метод получения списка доступных университетов."""
    program_service = ProgramService(db)
    status_code, content = program_service.get_available_universities()
    return JSONResponse(status_code=status_code, content=content)

@router.get("/get-available-export-formats")
def getAvailableExportFormats():
    """Метод получения списка доступных форматов для экспорта."""
    graph_service = GraphService(None, None, None)
    status_code, content = graph_service.get_available_export_formats()
    return JSONResponse(status_code=status_code, content=content)

@router.get("/download-graph")
def downloadGraph(format: str, graphId: str, user_id: int = Depends(get_current_user),
                  db: DataBaseController = Depends(get_db),
                  rdf: RdfController = Depends(get_rdf)):
    """Скачивание графа"""
    graph_service = GraphService(db, None, rdf)
    response = graph_service.get_export_file(format, graphId, user_id)
    return response

@router.get("/find-graph-bridges")
def findGraphBridges(graphId: str, db: DataBaseController = Depends(get_db),
                  rdf: RdfController = Depends(get_rdf)):
    """Нахождение мостов графа"""
    graph_service = GraphService(db, None, rdf)
    status_code, content = graph_service.find_graph_bridges(graphId)
    return JSONResponse(status_code=status_code, content=content)

@router.get("/download-report")
def downloadReport(format: str, graphId: str, user_id: int = Depends(get_current_user),
                   db: DataBaseController = Depends(get_db), 
                   rdf: RdfController = Depends(get_rdf)):
    """Скачивание отчета"""
    graph_service = GraphService(db, None, rdf)
    response = graph_service.get_report_file(format, graphId, user_id)
    return response

@router.get("/get-history")
def getHistory(user_id: int = Depends(get_current_user), db: DataBaseController = Depends(get_db)):
    """Метод истории сравнений."""
    program_service = ProgramService(db)
    status_code, content = program_service.get_history(user_id)
    return JSONResponse(status_code=status_code, content=content)

@router.get("/get-history-graph")
def getHistoryGraph(hash: str, user_id: int = Depends(get_current_user), 
                    rdf: RdfController = Depends(get_rdf),
                    db: DataBaseController = Depends(get_db)):
    """Метод истории сравнений."""
    program_service = ProgramService(db, rdf)
    status_code, content = program_service.get_history_graph(user_id, hash)
    return JSONResponse(status_code=status_code, content=content)


@router.post("/add-program-from-files")
async def add_program_from_files(
    files: list[UploadFile] = File(...),
    university_name: str = Form(...),
    program_name: str = Form(...),
    user_id: int = Depends(get_current_user),
    db: DataBaseController = Depends(get_db),
    rdf: RdfController = Depends(get_rdf)
):
    """Метод добавления учебной программы из файлов."""
    program_service = ProgramService(db, rdf)
    status_code, content = await program_service.add_program_from_files(files, university_name, program_name, user_id)
    return JSONResponse(status_code=status_code, content=content)


@router.post("/compare_graphs")
def compare_graphs(payload: Any = Body(...), user_id: int = Depends(get_current_user),
                   db: DataBaseController = Depends(get_db),
                   rdf: RdfController = Depends(get_rdf)):
    """Сравнение графов программ по подтемам (educational units)."""
    try:
        # использование user_id из токена
        university_name = payload.get("university_name")
        program_name = payload.get("program_name")
        compare_programs_raw = payload.get("compare_programs", []) or []

        compare_refs: List[ProgramReference] = []
        for item in compare_programs_raw:
            try:
                pr = ProgramReference.model_validate(item)
                compare_refs.append(pr)
            except Exception:
                continue

    except Exception as e:
        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            content={"responseMessage": "Invalid payload", "error": str(e)})

    if not isinstance(university_name, str) or not university_name.strip():
        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            content={"responseMessage": "Field 'university_name' is required"})
    if not isinstance(program_name, str) or not program_name.strip():
        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            content={"responseMessage": "Field 'program_name' is required"})

    llm = GigachatService()
    graph_service = GraphService(db, llm, rdf)
    status_code, content = graph_service.compare_graphs(user_id, university_name, program_name, compare_refs)
    return JSONResponse(status_code=status_code, content=content)