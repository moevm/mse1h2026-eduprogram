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
from src.services.gigachat_service import GigachatService
from src.dataBase.dataBaseStructs import ProgramReference
from typing import List
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
def getPrograms(userId: int, db: DataBaseController = Depends(get_db), rdf: RdfController = Depends(get_rdf)):
    """Метод получения списка программ пользователя."""
    program_service = ProgramService(db, rdf)
    status_code, content = program_service.get_programs(userId)
    return JSONResponse(status_code=status_code, content=content)


@router.get("/show-graph")
def getCertainProgram(userId: int, pathToProgramFolder: str, universityName: str | None = None,
                      db: DataBaseController = Depends(get_db),
                      rdf: RdfController = Depends(get_rdf)):
    """Метод получения графа учебной программы."""
    graph_service = GraphService(db, None, rdf)
    status_code, content = graph_service.get_certain_program(userId, pathToProgramFolder, universityName)
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
    program_service = GraphService(None, None, None)
    status_code, content = program_service.get_available_export_formats()
    return JSONResponse(status_code=status_code, content=content)

@router.get("/download-graph")
def downloadGraph(format: str, graphId: str, db: DataBaseController = Depends(get_db),
                             rdf: RdfController = Depends(get_rdf)):
    """Скачивание графа"""
    program_service = GraphService(db, None, rdf)
    response = program_service.get_export_file(format, graphId)
    return response

@router.get("/download-report")
def downloadGraph(format: str, graphId: str, db: DataBaseController = Depends(get_db), rdf: RdfController = Depends(get_rdf)):
    """Скачивание отчета"""
    program_service = GraphService(db, None, rdf)
    response = program_service.get_report_file(format, graphId)
    return response

@router.get("/get-history")
def getHistory(user_id: int, db: DataBaseController = Depends(get_db)):
    """Метод истории сравнений."""
    program_service = ProgramService(db)
    status_code, content = program_service.get_history(user_id)
    return JSONResponse(status_code=status_code, content=content)

@router.get("/get-history-graph")
def getHistoryGraph(user_id: int, hash: str, rdf: RdfController = Depends(get_rdf)):
    """Метод истории сравнений."""
    program_service = ProgramService(None, rdf)
    status_code, content = program_service.get_history_graph(user_id, hash)
    return JSONResponse(status_code=status_code, content=content)


@router.post("/add-program-from-files")
async def add_program_from_files(
    files: list[UploadFile] = File(...),
    university_name: str = Form(...),
    program_name: str = Form(...),
    id_user: int = Form(...),
    db: DataBaseController = Depends(get_db),
    rdf: RdfController = Depends(get_rdf)
):
    """Метод добавления учебной программы из файлов."""
    program_service = ProgramService(db, rdf)
    status_code, content = await program_service.add_program_from_files(files, university_name, program_name, id_user)
    return JSONResponse(status_code=status_code, content=content)


@router.post("/compare_graphs")
def compare_graphs(payload: Any = Body(...), db: DataBaseController = Depends(get_db),
                   rdf: RdfController = Depends(get_rdf)):
    """Сравнение графов программ по подтемам (educational units)."""
    try:
        user_id = payload.get("user_id") or payload.get("idUser")
        if user_id is None:
            return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                content={"responseMessage": "Field 'user_id' is required"})
        user_id = int(user_id)

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