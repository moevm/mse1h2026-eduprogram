from typing import Tuple, Dict, Any, Optional
from fastapi import status
from pathlib import Path
import os
import json
from src.dataBase.dataBaseController import DataBaseController
from src.rdf.rdf_controller import RdfController


class GraphService:
    """Сервис для работы с графами учебных программ."""

    def __init__(self, db: DataBaseController, rdf: Optional[RdfController] = None):
        self.db = db
        self.rdf = rdf
        self.path_storage = Path(os.getenv('LOCAL_PATH_TO_STORAGE'))

    @staticmethod
    def _resolve_university_and_program(path_to_program_folder: str,
                                        university_name: Optional[str]) -> Tuple[str, str]:
        program_name = str(path_to_program_folder or "").strip()
        resolved_university = str(university_name or "").strip()

        if not resolved_university and "," in program_name:
            left, right = [part.strip() for part in program_name.split(",", 1)]
            if left and right:
                resolved_university = left
                program_name = right

        if not resolved_university and "/" in program_name:
            left, right = [part.strip() for part in program_name.split("/", 1)]
            if left and right:
                resolved_university = left
                program_name = right

        if not resolved_university:
            resolved_university = "frontend"

        return resolved_university, program_name

    def get_certain_program(self, user_id: int, path_to_program_folder: str,
                            university_name: Optional[str] = None) -> Tuple[int, Dict[str, Any]]:
        """Получение определенной учебной программы."""

        # is_program_exist = self.db.checkWorkProgram(user_id, path_to_program_folder)
        # if not is_program_exist:
        #     return (
        #         status.HTTP_400_BAD_REQUEST,
        #         {"responseMessage": "Work program not found"}
        #     )
        #
        # work_program_path = self.path_storage / self.db.getWorkProgramPath(user_id, path_to_program_folder)
        #
        # if not work_program_path.is_file():
        #     return (
        #         status.HTTP_400_BAD_REQUEST,
        #         {"responseMessage": "Work program not found"}
        #     )

        try:
            # with open(work_program_path, 'r', encoding="utf-8") as file_work_program_json:
            #     program_data = json.load(file_work_program_json)

            resolved_university, program_name = self._resolve_university_and_program(
                path_to_program_folder, university_name)

            program_data = None
            if self.rdf:
                program_data = self.rdf.get_data_of_university_and_program(
                    resolved_university, program_name, user_id)

            if program_data is None:
                return (
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    {"responseMessage": "RDF repository query error"}
                )

            return (
                status.HTTP_200_OK,
                program_data
            )

        except Exception as ex:
            return (
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                {"responseMessage": f"Error reading file: {str(ex)}"}
            )