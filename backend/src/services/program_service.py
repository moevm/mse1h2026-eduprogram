from typing import Tuple, Dict, Any, List, Optional
from fastapi import status
from pathlib import Path
import os
import json
import tempfile
from src.dataBase.dataBaseController import DataBaseController
from src.dataBase.dataBaseStructs import WorkProgram, Topic
from src.rdf.rdf_controller import RdfController
from src.api.translator import translate_work_program_values
from src.configs import mapParsersFromTypeToObject


class ProgramService:
    """Сервис для работы с учебными программами."""

    def __init__(self, db: DataBaseController, rdf: Optional[RdfController] = None):
        self.db = db
        self.rdf = rdf
        self.path_storage = Path(os.getenv('LOCAL_PATH_TO_STORAGE'))

    def _upload_json_file(self, path_to_file: Path, content: Dict[str, Any]) -> Tuple[bool, bool]:
        """Атомарно сохраняет произвольный JSON в файл."""
        is_exist_directory_path = path_to_file.parent.exists()
        is_exist_file_path = path_to_file.exists()

        path_to_file.parent.mkdir(parents=True, exist_ok=True)

        with tempfile.NamedTemporaryFile('w', encoding='utf-8', delete=False, dir=str(path_to_file.parent),
                                         suffix='.tmp') as temp_file:
            json.dump(content, temp_file, indent=4, ensure_ascii=False)
            temp_path = Path(temp_file.name)

        os.replace(temp_path, path_to_file)

        return is_exist_directory_path, is_exist_file_path

    def _upload_file_work_program(self, path_work_program: Path, work_program: WorkProgram) -> Tuple[bool, bool]:
        """Метод загрузки файла учебной и создания папок с университетом и направлением"""
        is_exist_direction_path = False
        is_exist_work_program_path = False

        if path_work_program.parent.exists():
            is_exist_direction_path = True

        path_work_program.parent.mkdir(parents=True, exist_ok=True)

        topics_dictionary = {}
        for topic_name, topic_data in work_program.topics.items():
            topics_dictionary[topic_name] = {
                "subtopics": topic_data.educationalUnits
            }

        program_work_dictionary = {
            work_program.nameDirection: {
                work_program.nameWorkProgram: {
                    "previousDisciplines": work_program.previousDisciplines,
                    "topics": topics_dictionary
                }
            }
        }

        if path_work_program.exists():
            is_exist_work_program_path = True

        with tempfile.NamedTemporaryFile('w', encoding='utf-8', delete=False, dir=str(path_work_program.parent),
                                         suffix='.tmp') as temp_file:
            json.dump(program_work_dictionary, temp_file, indent=4, ensure_ascii=False)
            temp_path = Path(temp_file.name)

        os.replace(temp_path, path_work_program)

        return is_exist_direction_path, is_exist_work_program_path

    def _parse_front_work_program_payload(self, payload: Dict[str, Any]) -> List[WorkProgram]:
        """Преобразует payload фронтенда в список WorkProgram."""
        if "idUser" not in payload:
            raise ValueError("Field 'idUser' is required")

        id_user = payload.get("idUser")
        if not isinstance(id_user, int):
            raise ValueError("Field 'idUser' must be integer")

        name_university = payload.get("nameUniversity", "frontend")
        if not isinstance(name_university, str) or not name_university.strip():
            name_university = "frontend"

        name_direction_override = payload.get("nameDirection")

        meta_keys = {"idUser", "nameUniversity", "nameDirection"}
        program_entries = [(k, v) for k, v in payload.items() if k not in meta_keys]
        if len(program_entries) != 1:
            raise ValueError("Payload must contain exactly one program root key")

        root_program_name, disciplines = program_entries[0]
        if not isinstance(disciplines, list):
            raise ValueError("Program value must be a list of disciplines")

        name_direction = name_direction_override or root_program_name
        result: List[WorkProgram] = []

        for discipline_item in disciplines:
            if not isinstance(discipline_item, dict) or len(discipline_item) != 1:
                raise ValueError("Each discipline item must be an object with one key")

            discipline_name, discipline_data = next(iter(discipline_item.items()))
            if not isinstance(discipline_data, dict):
                raise ValueError("Discipline data must be an object")

            previous_disciplines = discipline_data.get("previousDisciplines", [])
            if not isinstance(previous_disciplines, list):
                raise ValueError("previousDisciplines must be a list")

            topics_payload = discipline_data.get("topics", [])
            if not isinstance(topics_payload, list):
                raise ValueError("topics must be a list")

            topics: Dict[str, Topic] = {}
            for topic_item in topics_payload:
                if not isinstance(topic_item, dict):
                    continue
                for topic_name, educational_units in topic_item.items():
                    if not isinstance(educational_units, list):
                        continue
                    topics[str(topic_name)] = Topic(educationalUnits=[str(unit) for unit in educational_units])

            result.append(
                WorkProgram(
                    idUser=id_user,
                    nameUniversity=str(name_university),
                    nameDirection=str(name_direction),
                    nameWorkProgram=str(discipline_name),
                    previousDisciplines=[str(item) for item in previous_disciplines],
                    topics=topics,
                )
            )

        if not result:
            raise ValueError("No work programs in payload")

        return result

    def add_program(self, payload: Any) -> Tuple[int, Dict[str, Any]]:
        """Метод добавления учебной программы.
        Возвращает код и ответ в формате.
        {responseMessage: {сообщение от сервера}}"""

        if not self.db.isConnected():
            return (
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                {"responseMessage": "DataBase connect error!"}
            )

        is_front_payload = isinstance(payload, dict) and "nameWorkProgram" not in payload

        try:
            if is_front_payload:
                if "idUser" not in payload or not isinstance(payload["idUser"], int):
                    raise ValueError("Field 'idUser' is required and must be integer")
                id_user = payload["idUser"]
            else:
                work_programs = [WorkProgram.model_validate(payload)]
                id_user = work_programs[0].idUser
        except Exception as error:
            return (
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                {"responseMessage": "Invalid add-program payload", "error": str(error)}
            )

        user = self.db.findUserById(id_user)
        if len(user) == 0:
            return (
                status.HTTP_401_UNAUTHORIZED,
                {"responseMessage": "Not find current user!"}
            )

        translation_warnings: List[str] = []

        if is_front_payload:
            name_university = payload.get("nameUniversity", "frontend")
            if not isinstance(name_university, str) or not name_university.strip():
                name_university = "frontend"

            name_direction_override = payload.get("nameDirection")
            if name_direction_override is not None and (
                    not isinstance(name_direction_override, str) or not name_direction_override.strip()):
                return (
                    status.HTTP_422_UNPROCESSABLE_ENTITY,
                    {"responseMessage": "Invalid add-program payload",
                     "error": "Field 'nameDirection' must be non-empty string"}
                )

            meta_keys = {"idUser", "nameUniversity", "nameDirection"}
            program_entries = [(k, v) for k, v in payload.items() if k not in meta_keys]
            if len(program_entries) != 1:
                return (
                    status.HTTP_422_UNPROCESSABLE_ENTITY,
                    {"responseMessage": "Invalid add-program payload",
                     "error": "Payload must contain exactly one program root key"}
                )

            root_program_name, disciplines = program_entries[0]
            if not isinstance(root_program_name, str) or not root_program_name.strip() or not isinstance(disciplines,
                                                                                                         list):
                return (
                    status.HTTP_422_UNPROCESSABLE_ENTITY,
                    {"responseMessage": "Invalid add-program payload",
                     "error": "Program root key must be string and value must be list"}
                )

            name_direction = name_direction_override or root_program_name
            final_program_json: Dict[str, Any] = {root_program_name: {}}
            translated_fields_count = 0

            for discipline_item in disciplines:
                if not isinstance(discipline_item, dict) or len(discipline_item) != 1:
                    continue

                discipline_name, discipline_data = next(iter(discipline_item.items()))
                if not isinstance(discipline_data, dict):
                    continue

                previous_disciplines = discipline_data.get("previousDisciplines", [])
                topics_payload = discipline_data.get("topics", [])
                if not isinstance(previous_disciplines, list):
                    previous_disciplines = []
                if not isinstance(topics_payload, list):
                    topics_payload = []

                topics_for_translate: Dict[str, Topic] = {}
                for topic_item in topics_payload:
                    if not isinstance(topic_item, dict):
                        continue
                    for topic_name, subtopics in topic_item.items():
                        if isinstance(subtopics, list):
                            topics_for_translate[str(topic_name)] = Topic(
                                educationalUnits=[str(unit) for unit in subtopics])

                work_program_for_translate = WorkProgram(
                    idUser=id_user,
                    nameUniversity=str(name_university),
                    nameDirection=str(name_direction),
                    nameWorkProgram=str(discipline_name),
                    previousDisciplines=[str(item) for item in previous_disciplines],
                    topics=topics_for_translate,
                )

                try:
                    translated_program, translation_stats = translate_work_program_values(work_program_for_translate)
                    translated_fields_count += translation_stats.translated_fields_count
                except Exception as error:
                    translated_program = work_program_for_translate
                    translation_warnings.append(str(error))

                final_program_json[root_program_name][translated_program.nameWorkProgram] = {
                    "previousDisciplines": translated_program.previousDisciplines,
                    "topics": {
                        topic_name: {"subtopics": topic_data.educationalUnits}
                        for topic_name, topic_data in translated_program.topics.items()
                    }
                }

            if self.rdf:
                self.rdf.add_program(name_university, payload, id_user)

            path_work_program = Path(name_university) / name_direction / f"{root_program_name}_{id_user}.json"
            is_exist_direction_path, is_exist_work_program_path = self._upload_json_file(
                self.path_storage / path_work_program, final_program_json)

            if not is_exist_direction_path:
                add_result = self.db.addUserFolder(id_user, str(path_work_program.parent))
                if not add_result:
                    return (
                        status.HTTP_500_INTERNAL_SERVER_ERROR,
                        {"responseMessage": "DataBase add user folder error!"}
                    )

            add_result = self.db.upsertWorkProgram(id_user, str(path_work_program.parent), str(path_work_program))
            if not add_result:
                return (
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    {"responseMessage": "DataBase add/update user file error!"}
                )

            return (
                status.HTTP_200_OK,
                {
                    "responseMessage": "ok",
                    "savedCount": 1,
                    "isOverwritten": is_exist_work_program_path,
                    "savedFilePath": str(path_work_program),
                    "savedFilePaths": [str(path_work_program)],
                    "translatedFieldsCount": translated_fields_count,
                    "translationSkipped": len(translation_warnings) > 0,
                    "translationWarnings": translation_warnings
                }
            )

        saved_paths: List[str] = []
        overwritten_count = 0
        translated_fields_count = 0

        for work_program in work_programs:
            try:
                translated_program, translation_stats = translate_work_program_values(work_program)
                translated_fields_count += translation_stats.translated_fields_count
            except Exception as error:
                translated_program = work_program
                translation_warnings.append(str(error))

            path_work_program = (Path(work_program.nameUniversity) / work_program.nameDirection /
                                 f"{work_program.nameWorkProgram}_{work_program.idUser}.json")
            is_exist_direction_path, is_exist_work_program_path = self._upload_file_work_program(
                self.path_storage / path_work_program, translated_program)

            if is_exist_work_program_path:
                overwritten_count += 1

            if not is_exist_direction_path:
                add_result = self.db.addUserFolder(translated_program.idUser, str(path_work_program.parent))
                if not add_result:
                    return (
                        status.HTTP_500_INTERNAL_SERVER_ERROR,
                        {"responseMessage": "DataBase add user folder error!"}
                    )

            add_result = self.db.upsertWorkProgram(translated_program.idUser, str(path_work_program.parent),
                                                   str(path_work_program))
            if not add_result:
                return (
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    {"responseMessage": "DataBase add/update user file error!"}
                )

            saved_paths.append(str(path_work_program))

        return (
            status.HTTP_200_OK,
            {
                "responseMessage": "ok",
                "savedCount": len(saved_paths),
                "isOverwritten": overwritten_count > 0,
                "savedFilePath": saved_paths[0] if saved_paths else "",
                "savedFilePaths": saved_paths,
                "translatedFieldsCount": translated_fields_count,
                "translationSkipped": len(translation_warnings) > 0,
                "translationWarnings": translation_warnings
            }
        )

    def get_programs(self, user_id: int) -> Tuple[int, Dict[str, Any]]:
        """Получение списка программ пользователя."""
        if not self.db.isConnected():
            return (
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                {"responseMessage": "DataBase connect error!"}
            )

        programs = self.db.getWorkPrograms(user_id)

        return (
            status.HTTP_200_OK,
            {"programs": programs}
        )

    def get_available_universities(self) -> Tuple[int, Dict[str, Any]]:
        """Получение списка доступных университетов."""
        if not self.db.isConnected():
            return (
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                {"responseMessage": "DataBase connect error!"}
            )

        result_list = []
        for type_name in mapParsersFromTypeToObject:
            university = self.db.findParserByType(type_name)
            if university:
                result_list.append(university)

        return (
            status.HTTP_200_OK,
            {"available-universities": result_list}
        )

    async def add_program_from_files(
            self,
            files: List,
            university_name: str,
            program_name: str,
            id_user: int
    ) -> Tuple[int, Dict[str, Any]]:
        """Метод добавления учебной программы из файлов."""

        if not self.db.isConnected():
            return (
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                {"responseMessage": "DataBase connection error!"}
            )

        user = self.db.findUserById(id_user)
        if len(user) == 0:
            return (
                status.HTTP_401_UNAUTHORIZED,
                {"responseMessage": "Invalid user!"}
            )

        parser_type = self.db.findTypeParserByUniversityName(university_name)
        if parser_type is None:
            return (
                status.HTTP_400_BAD_REQUEST,
                {"responseMessage": f"Parser for university '{university_name}' does not exist!"}
            )

        files_data = []
        for file in files:
            file_bytes = await file.read()
            files_data.append((file.filename, file_bytes))

        parser_class = mapParsersFromTypeToObject[parser_type]
        parser = parser_class()
        result = parser.parse(files_data, program_name)

        has_disciplines = any(
            isinstance(value, list) and len(value) > 0 for value in result.values()
        ) if isinstance(result, dict) else False

        if not result or not isinstance(result, dict) or not has_disciplines:
            return (
                status.HTTP_400_BAD_REQUEST,
                {"responseMessage": "Files parsing failed!"}
            )

        path_work_program = Path(university_name) / f"{university_name}_{id_user}.json"
        is_exist_direction_path, is_exist_file_path = self._upload_json_file(self.path_storage / path_work_program,
                                                                             result)

        if self.rdf:
            self.rdf.add_program(university_name, result, id_user)

        if not is_exist_direction_path:
            add_result = self.db.addUserFolder(id_user, str(path_work_program.parent))
            if not add_result:
                return (
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    {"responseMessage": "DataBase adding in user folder error!"}
                )

        add_result = self.db.upsertWorkProgram(id_user, str(path_work_program.parent), str(path_work_program))
        if not add_result:
            return (
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                {"responseMessage": "DataBase add/update user file error!"}
            )

        return (
            status.HTTP_200_OK,
            {
                "responseMessage": "ok",
                "savedCount": 1,
                "isOverwritten": is_exist_file_path,
                "savedFilePath": str(path_work_program),
                "savedFilePaths": [str(path_work_program)]
            }
        )