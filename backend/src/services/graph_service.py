from typing import Tuple, Dict, Any, Optional, List, Set
from fastapi import status
from pathlib import Path
import os
import json
import re
from difflib import SequenceMatcher
from src.dataBase.dataBaseController import DataBaseController
from src.dataBase.dataBaseStructs import ProgramReference
from src.rdf.rdf_controller import RdfController
from src.services.gigachat_service import GigachatService
from src.utils.gigachat_matcher import GigachatMatcher


class GraphService:
    """Сервис для работы с графами учебных программ."""

    def __init__(self, db: DataBaseController, llm: GigachatService, rdf: Optional[RdfController]):
        self.db = db
        self.rdf = rdf
        self.path_storage = Path(os.getenv('LOCAL_PATH_TO_STORAGE'))
        self.gigachat = GigachatMatcher(llm)

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

    @staticmethod
    def _normalize_text(value: str) -> str:
        value = str(value or "").lower().strip()
        value = value.replace("ё", "е")
        value = re.sub(r"[^a-zа-я0-9]+", " ", value)
        return re.sub(r"\s+", " ", value).strip()

    def _normalize_program_structure(self, program: Dict[str, Any] | None) -> Dict[str, Any]:
        if not program:
            return {}

        try:
            program_name = next(iter(program.keys()))
            disciplines = program.get(program_name, {})

            if isinstance(disciplines, dict):
                disciplines = [{name: data} for name, data in disciplines.items()]

            if not isinstance(disciplines, list):
                return {}

            normalized_disciplines: Dict[str, Any] = {}
            for discipline_item in disciplines:
                if not isinstance(discipline_item, dict):
                    continue
                for discipline_name, discipline_data in discipline_item.items():
                    if not isinstance(discipline_data, dict):
                        continue
                    normalized_disciplines[str(discipline_name)] = {
                        "previousDisciplines": list(discipline_data.get("previousDisciplines", []) or []),
                        "topics": discipline_data.get("topics", {}) or {}
                    }

            return {str(program_name): normalized_disciplines}
        except Exception:
            return {}

    def _iter_topics(self, discipline_data: Dict[str, Any]) -> List[Tuple[str, List[str]]]:
        topics = discipline_data.get("topics", {}) or {}
        result: List[Tuple[str, List[str]]] = []

        if isinstance(topics, dict):
            topic_items = topics.items()
        elif isinstance(topics, list):
            topic_items = []
            for item in topics:
                if isinstance(item, dict):
                    topic_items.extend(item.items())
        else:
            topic_items = []

        for topic_name, topic_value in topic_items:
            subtopics: List[str] = []
            if isinstance(topic_value, dict):
                if "subtopics" in topic_value:
                    subtopics_value = topic_value["subtopics"]
                    if isinstance(subtopics_value, dict):
                        subtopics = [str(name) for name in subtopics_value.keys()]
                    elif isinstance(subtopics_value, list):
                        subtopics = [str(item) for item in subtopics_value]
                else:
                    subtopics = [str(name) for name in topic_value.keys()]
            elif isinstance(topic_value, list):
                subtopics = [str(item) for item in topic_value]

            result.append((str(topic_name), subtopics))

        return result

    def _extract_subtopics_index(self, program: Dict[str, Any]) -> Dict[str, Set[str]]:
        program_name = next(iter(program.keys()), None)
        if not program_name:
            return {}

        disciplines = program.get(program_name, {}) or {}
        index: Dict[str, Set[str]] = {}

        for discipline_name, discipline_data in disciplines.items():
            topic_subtopics: Set[str] = set()
            for _, subtopics in self._iter_topics(discipline_data):
                topic_subtopics.update(subtopics)
            index[str(discipline_name)] = topic_subtopics

        return index

    def _subtopic_similarity(self, left: str, right: str) -> float:
        left_norm = self._normalize_text(left)
        right_norm = self._normalize_text(right)

        if not left_norm or not right_norm:
            return 0.0
        if left_norm == right_norm:
            return 1.0
        if left_norm in right_norm or right_norm in left_norm:
            return 0.9

        left_tokens = set(left_norm.split())
        right_tokens = set(right_norm.split())
        if left_tokens and right_tokens:
            token_score = len(left_tokens & right_tokens) / max(1, min(len(left_tokens), len(right_tokens)))
            if token_score >= 0.5:
                return max(0.75, token_score)

        sequence_score = SequenceMatcher(None, left_norm, right_norm).ratio()
    
        if sequence_score < 0.75 and sequence_score >= 0.3 and self.gigachat:
            try:
                llm_result = self.gigachat.check_subtopic_similarity(left, right)
                if llm_result:
                    return 0.9
            except Exception as e:
                print(f"LLM check failed for '{left}' vs '{right}': {e}")
    
        return sequence_score

    def _best_subtopic_overlap(self, target_subtopic: str, compare_programs: List[Dict[str, Any]]) -> int:
        if not compare_programs:
            return 0

        matched_programs = 0
        for compare_program in compare_programs:
            compare_index = self._extract_subtopics_index(compare_program)
            found = False
            for subtopics in compare_index.values():
                for candidate in subtopics:
                    if self._subtopic_similarity(target_subtopic, candidate) >= 0.75:
                        found = True
                        break
                if found:
                    break
            if found:
                matched_programs += 1

        return int(round((matched_programs / len(compare_programs)) * 100))

    def _find_missing_subtopics(
                            self, 
                            target_program: Dict[str, Any], 
                            compare_payloads: List[Dict[str, Any]],
                            threshold: int = 70
    ) -> List[Tuple[str, str, int]]:
        """
        Находит подтемы из сравниваемых программ, отсутствующие в целевой.
        Возвращает: [(subtopic, discipline, overlap_percent), ...]
        """
        target_index = self._extract_subtopics_index(target_program)
        target_all_subtopics: Set[str] = set()
        for subtopics in target_index.values():
            target_all_subtopics.update(subtopics)
    
        from collections import Counter
    
        foreign_subtopic_counts: Dict[str, Tuple[int, str]] = {}  # subtopic -> (count, discipline)
    
        for compare_program in compare_payloads:
            program_name = next(iter(compare_program.keys()), "")
            compare_index = self._extract_subtopics_index(compare_program)
        
            for discipline_name, subtopics in compare_index.items():
                for candidate in subtopics:
                    found_in_target = False
                    for target_subtopic in target_all_subtopics:
                        if self._subtopic_similarity(candidate, target_subtopic) >= 0.75:
                            found_in_target = True
                            break
                
                    if not found_in_target:
                        if candidate not in foreign_subtopic_counts:
                            foreign_subtopic_counts[candidate] = [0, discipline_name]
                        foreign_subtopic_counts[candidate][0] += 1
    
        total_programs = len(compare_payloads)
    
        missing: List[Tuple[str, str, int]] = []
        for subtopic, (count, discipline) in foreign_subtopic_counts.items():
            overlap_percent = int(round((count / total_programs) * 100))
            if overlap_percent >= threshold:
                missing.append((subtopic, discipline, overlap_percent))
    
        missing.sort(key=lambda x: x[2], reverse=True)
    
        return missing

    def compare_graphs(self, user_id: int, university_name: str, program_name: str,
                       compare_programs: List[ProgramReference]) -> Tuple[int, Dict[str, Any]]:
        if not self.rdf:
            return (
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                {"responseMessage": "RDF repository is not available"}
            )
        target_program = self.rdf.get_data_of_university_and_program(university_name, program_name, user_id)
        target_program = self._normalize_program_structure(target_program)

        if not target_program:
            return (
                status.HTTP_404_NOT_FOUND,
                {"responseMessage": "Target program not found"}
            )

        compare_payloads: List[Dict[str, Any]] = []
        for reference in compare_programs or []:
            if not reference.university_name or not reference.program_name:
                continue
            program_data = self.rdf.get_data_of_university_and_program(
                reference.university_name,
                reference.program_name,
                user_id,
            )
            normalized_program = self._normalize_program_structure(program_data)
            if normalized_program:
                compare_payloads.append(normalized_program)

        target_program_name = next(iter(target_program.keys()))
        target_disciplines = target_program.get(target_program_name, {}) or {}

        formatted_disciplines: List[Dict[str, Any]] = []
        recommendations: List[str] = []

        for discipline_name, discipline_data in target_disciplines.items():
            topics_result: List[Dict[str, Any]] = []
            low_overlap_subtopics: List[str] = []
            high_overlap_subtopics: List[str] = []

            for topic_name, subtopics in self._iter_topics(discipline_data):
                topic_result: List[Dict[str, Any]] = []
                for subtopic_name in subtopics:
                    overlap_value = self._best_subtopic_overlap(subtopic_name, compare_payloads)
                    topic_result.append({subtopic_name: {"overlapValue": overlap_value}})

                    if overlap_value <= 35:
                        low_overlap_subtopics.append(subtopic_name)
                    elif overlap_value >= 70:
                        high_overlap_subtopics.append(subtopic_name)

                topics_result.append({topic_name: topic_result})

            formatted_disciplines.append({
                discipline_name: {
                    "previousDisciplines": list(discipline_data.get("previousDisciplines", []) or []),
                    "topics": topics_result,
                }
            })

            for subtopic_name in low_overlap_subtopics:
                recommendations.append(
                    f"Стоит убрать учебную единицу '{subtopic_name}' из дисциплины '{discipline_name}'"
                )

        missing_subtopics = self._find_missing_subtopics(target_program, compare_payloads, threshold=70)
        for subtopic_name, discipline_name, overlap_percent in missing_subtopics:
            recommendations.append(
            f"Учебная единица '{subtopic_name}' (встречается в {overlap_percent}% "
            f"сравниваемых программ, дисциплина '{discipline_name}') отсутствует "
            f"в целевой программе — рекомендуется добавить"
        )

        if not recommendations:
            recommendations.append("Сравнение выполнено, явных расхождений не найдено")

        return (
            status.HTTP_200_OK,
            {
                target_program_name: formatted_disciplines,
                "Recomendations": recommendations,
            }
        )