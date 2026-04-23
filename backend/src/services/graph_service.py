from typing import Tuple, Dict, Any
from fastapi import status
from pathlib import Path
import os
import json
from src.dataBase.dataBaseController import DataBaseController


class GraphService:
    """Сервис для работы с графами учебных программ."""

    def __init__(self, db: DataBaseController):
        self.db = db
        self.path_storage = Path(os.getenv('LOCAL_PATH_TO_STORAGE'))

    def get_certain_program(self, user_id: int, path_to_program_folder: str) -> Tuple[int, Dict[str, Any]]:
        """Получение определенной учебной программы."""

        is_program_exist = self.db.checkWorkProgram(user_id, path_to_program_folder)
        if not is_program_exist:
            return (
                status.HTTP_400_BAD_REQUEST,
                {"responseMessage": "Work program not found"}
            )

        work_program_path = self.path_storage / self.db.getWorkProgramPath(user_id, path_to_program_folder)

        if not work_program_path.is_file():
            return (
                status.HTTP_400_BAD_REQUEST,
                {"responseMessage": "Work program not found"}
            )

        try:
            with open(work_program_path, 'r', encoding="utf-8") as file_work_program_json:
                program_data = json.load(file_work_program_json)

            return (
                status.HTTP_200_OK,
                program_data
            )

        except Exception as ex:
            return (
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                {"responseMessage": f"Error reading file: {str(ex)}"}
            )