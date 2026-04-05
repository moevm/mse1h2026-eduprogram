from __future__ import annotations

import os
import re
from collections import OrderedDict
from typing import Any
from pymupdf import pymupdf

class ParserGUAP:
    """Парсер РПД ГУАП для сценария с загрузкой PDF через FastAPI.

    Сейчас у класса одна публичная функция: parse().
    Она принимает список файлов в виде пар `(filename, bytes)` и название
    образовательной программы, а возвращает JSON в формате:

    {
      "Название образовательной программы": [
        {
          "Дисциплина": {
            "previousDisciplines": ["..."],
            "topics": []
          }
        }
      ]
    }
    """

    def __init__(self) -> None:
        self.__bad_starts = [
            "—", "«", "", "●", "•", "–", "-", "_", "", "",
            "в", "на", "при", "для", "и", "с", "со", "к", "по", "из", "за",
            "над", "под", "об", "от", "так", "также", "а", "но", "или",
        ]

    def parse(
        self,
        files: list[tuple[str, bytes]],
        educational_program_name: str,
    ) -> dict[str, list[dict[str, Any]]]:
        """Парсит набор PDF-файлов и возвращает итоговый JSON-словарь."""
        disciplines: list[dict[str, Any]] = []

        for file_name, file_bytes in files:
            discipline_name, previous_disciplines, topics = self._read_discipline_from_bytes(
                file_name=file_name,
                file_bytes=file_bytes,
            )

            if not discipline_name:
                continue

            disciplines.append(
                {
                    discipline_name: {
                        "previousDisciplines": previous_disciplines,
                        "topics": topics,
                    }
                }
            )

        return {educational_program_name: disciplines}

    def _read_discipline_from_bytes(
        self,
        file_name: str,
        file_bytes: bytes,
    ) -> tuple[str, list[str], list[dict[str, Any]]]:
        """Извлекает название дисциплины, список предыдущих дисциплин и темы из PDF."""
        if not isinstance(file_bytes, (bytes, bytearray)):
            return "", [], []

        try:
            full_text = self._extract_text_from_pdf_bytes(bytes(file_bytes))
        except Exception:
            return "", [], []

        discipline_name = self._extract_discipline_name(full_text, file_name)
        if not discipline_name:
            return "", [], []

        previous_disciplines = self._extract_previous_disciplines(full_text)
        topics = self._extract_topics(full_text)
        return discipline_name, previous_disciplines, topics

    def _extract_text_from_pdf_bytes(self, file_bytes: bytes) -> str:
        """Извлекает текст со всех страниц PDF-документа."""
        full_text = []
        document = pymupdf.open(stream=file_bytes, filetype="pdf")

        try:
            for page in document:
                page_text = page.get_text()
                if page_text:
                    full_text.append(page_text)
        finally:
            document.close()

        return "\n".join(full_text)

    def _extract_discipline_name(self, text: str, file_name: str) -> str:
        """Извлекает название дисциплины из текста PDF или из имени файла."""
        patterns = [
            r'РАБОЧАЯ ПРОГРАММА ДИСЦИПЛИНЫ\s*[«"]\s*([^»"]+)\s*[»"]',
            r'Дисциплина\s*[«"]\s*([^»"]+)\s*[»"]',
            r'Дисциплина\s+([А-Яа-яA-Za-z\s\-]+?)\s+входит',
            r'Дисциплина\s+([А-Яа-яA-Za-z\s\-]+?)\s+реализуется',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name = self._clean_text(match.group(1))
                if name and len(name) > 3:
                    return name

        filename = os.path.splitext(os.path.basename(file_name))[0]
        filename = re.sub(r'^rpd_', '', filename, flags=re.IGNORECASE)
        filename = re.sub(r'_\d+$', '', filename)
        filename = filename.replace('_', ' ').strip()
        return self._clean_text(filename).title()

    def _extract_previous_disciplines(self, text: str) -> list[str]:
        """Извлекает список дисциплин, которые нужны до изучения текущей."""
        section_patterns = [
            r'2\.\s*Место дисциплины в структуре ОП(.*?)(?=\n\d+\.|\Z)',
            r'2\.\s*Место дисциплины в структуре образовательной программы(.*?)(?=\n\d+\.|\Z)',
            r'2\.\s*Место дисциплины.*?(.*?)(?=\n\d+\.|\Z)',
        ]

        section_text = ""
        for pattern in section_patterns:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                section_text = match.group(1)
                break

        if not section_text:
            return []

        if re.search(r'не\s+базир\w*\s+на\s+знани\w*', section_text, re.IGNORECASE):
            return []

        anchor_pattern = r'при\s+изучении\s+следующ\w*\s+дисциплин\s*[:\-]?\s*'
        anchor_match = re.search(anchor_pattern, section_text, re.IGNORECASE)

        if not anchor_match:
            return []

        tail = section_text[anchor_match.end():]
        boundary_match = re.search(
            r'\n\s*[−–•\*\-]*\s*(Знания\s*,?\s*полученн\w*|3\.)',
            tail,
            re.IGNORECASE,
        )
        previous_block = tail[:boundary_match.start()] if boundary_match else tail

        return self._clean_discipline_list(self._extract_list_items(previous_block))

    def _extract_topics(self, text: str) -> list[dict[str, Any]]:
        """Извлекает основные разделы и темы из раздела 4."""
        candidate_sections = [
            self._extract_section_text(
                text,
                start_patterns=[
                    r'4\.2\.\s*Содержание разделов и тем лекционных занятий',
                    r'4\.2\.\s*Содержание разделов и тем',
                    r'4\.2\.',
                ],
                end_pattern=r'\b4\.3\.\b|\b4\.4\.\b|\b5\.\s+|\bИтого\b',
            ),
            self._extract_section_text(
                text,
                start_patterns=[
                    r'4\.1\.\s*Распределение трудоемкости дисциплины по разделам и видам занятий',
                    r'4\.1\.\s*Распределение трудоемкости',
                    r'4\.1\.',
                ],
                end_pattern=r'\b4\.2\.\b|\bИтого\b|\bПрактическая\s+подготовка\b|(?:^|\n)\s*[5-9]\.\s+(?!\d)',
            ),
            self._extract_section_text(
                text,
                start_patterns=[
                    r'4\.\s*Содержание дисциплины',
                    r'4\.\s*Содержание',
                ],
                end_pattern=r'\b4\.3\.\b|\b4\.4\.\b|\b5\.\s+|\bИтого\b',
            ),
        ]

        best_topics: list[dict[str, Any]] = []
        best_score = -1.0

        for section_text in candidate_sections:
            parsed_topics = self._parse_topic_block(section_text)
            if not parsed_topics:
                continue

            score = self._score_topics(parsed_topics)
            if score > best_score:
                best_topics = parsed_topics
                best_score = score

        return best_topics

    def _score_topics(self, topics: list[dict[str, Any]]) -> float:
        """Оценивает качество извлеченных тем: больше тем и меньше мусора -> выше балл."""
        if not topics:
            return 0.0

        score = float(len(topics))
        for item in topics:
            title, subtopics = next(iter(item.items()))
            title_lower = title.lower()

            if len(title) > 200:
                score -= 4.0
            if re.search(r'итого|таблица|содержание\s+разделов|практическая\s+подготовка', title_lower):
                score -= 8.0
            if re.search(r'\b\d{2,}\b', title):
                score -= 1.0

            score += min(len(subtopics), 6) * 0.4

        return score

    def _parse_topic_block(self, section_text: str) -> list[dict[str, Any]]:
        """Парсит готовый фрагмент текста раздела 4 в структуру разделов и тем."""
        line_topics = self._parse_topic_block_by_lines(section_text)

        if not section_text:
            return line_topics

        section_text = re.sub(
            r'\b(Раздел|Тема)\s*\n\s*(\d+(?:\.\d+)*\.?)',
            lambda match: f'{match.group(1)} {match.group(2)}',
            section_text,
            flags=re.IGNORECASE,
        )

        compact_text = self._clean_text(section_text)
        if not compact_text:
            return []

        marker_regex = re.compile(
            r'\b(?P<kind>Раздел|Тема)\s+(?P<num>\d+(?:\.\d+)*)(?P<dot>\.)?',
            re.IGNORECASE,
        )

        markers = list(marker_regex.finditer(compact_text))
        if not markers:
            return []

        sections: OrderedDict[str, dict[str, Any]] = OrderedDict()
        current_section_key = "4"
        current_section = None

        for index, marker in enumerate(markers):
            kind = marker.group('kind').lower()
            number = marker.group('num')
            next_start = markers[index + 1].start() if index + 1 < len(markers) else len(compact_text)
            content = self._clean_text(compact_text[marker.end():next_start])
            title = self._build_topic_title(kind, number, content)

            if not title or re.fullmatch(r'^\d+(?:\.\d+)*$', title.strip()):
                continue


            if kind == 'раздел':
                if not self._is_valid_topic(title):
                    current_section = None
                    continue

                section_key = number
                current_section_key = section_key
                current_section = sections.get(section_key)

                if current_section is None:
                    current_section = {
                        "title": title,
                        "subtopics": [],
                    }
                    sections[section_key] = current_section
                elif len(title) > len(current_section["title"]):
                    current_section["title"] = title

                continue

            if current_section is None:
                current_section = sections.get(current_section_key)
                if current_section is None:
                    if not self._is_valid_topic(title):
                        continue
                    current_section = {
                        "title": "Содержание дисциплины",
                        "subtopics": [],
                    }
                    sections[current_section_key] = current_section

            if self._is_valid_topic(title):
                normalized_title = re.sub(r'\s+', ' ', title).strip().lower()
                normalized_subtopics = {
                    re.sub(r'\s+', ' ', item).strip().lower()
                    for item in current_section["subtopics"]
                }
                if normalized_title not in normalized_subtopics:
                    current_section["subtopics"].append(title)

        formatted_topics: list[dict[str, list[str]]] = []
        for section in sections.values():
            title = section.get("title", "").strip()
            if not title:
                continue
            formatted_topics.append({title: section["subtopics"]})

        if self._score_topics(line_topics) > self._score_topics(formatted_topics):
            return line_topics

        return formatted_topics

    def _parse_topic_block_by_lines(self, section_text: str) -> list[dict[str, Any]]:
        """Парсит темы из табличного текста в строковом режиме (устойчиво к OCR-склейкам)."""
        if not section_text:
            return []

        raw_lines = [line.strip() for line in section_text.splitlines() if line.strip()]
        if not raw_lines:
            return []

        sections: list[dict[str, Any]] = []
        current_section: dict[str, Any] | None = None

        i = 0
        while i < len(raw_lines):
            line = raw_lines[i]
            line_lower = line.lower()

            if re.search(r'\b(итого|практическая\s+подготовка|таблица|содержание\s+разделов)\b', line_lower):
                break

            if re.fullmatch(r'[\d\s.,\-–—]+', line):
                i += 1
                continue

            section_match = re.match(r'^Раздел\s*(\d+)\.?(.*)$', line, re.IGNORECASE)
            if section_match:
                title_part = section_match.group(2).strip()

                # Иногда заголовок раздела переносится на следующую строку.
                if (not title_part) and i + 1 < len(raw_lines):
                    nxt = raw_lines[i + 1].strip()
                    if nxt and not re.match(r'^(Раздел\s*\d+|\d+\.\d+\.?|\d+)$', nxt, re.IGNORECASE):
                        title_part = nxt
                        i += 1

                title = self._sanitize_topic_text(title_part)
                if title and self._is_valid_topic(title):
                    current_section = {"title": title, "subtopics": []}
                    sections.append(current_section)

                i += 1
                continue

            # Формат таблицы 4.2: отдельная строка с номером раздела и следующая строка с названием.
            if re.fullmatch(r'\d+', line) and i + 1 < len(raw_lines):
                nxt = raw_lines[i + 1].strip()
                if nxt and not re.match(r'^(\d+\.\d+\.?|\d+)$', nxt):
                    title = self._sanitize_topic_text(nxt)
                    if title and self._is_valid_topic(title):
                        current_section = {"title": title, "subtopics": []}
                        sections.append(current_section)
                    i += 2
                    continue

            topic_match = re.match(r'^\d+\.\d+\.?\s*(.*)$', line)
            if topic_match and current_section is not None:
                subtopic = self._sanitize_topic_text(topic_match.group(1))
                if subtopic and self._is_valid_topic(subtopic):
                    normalized = re.sub(r'\s+', ' ', subtopic).strip().lower()
                    existing = {
                        re.sub(r'\s+', ' ', item).strip().lower()
                        for item in current_section["subtopics"]
                    }
                    if normalized not in existing:
                        current_section["subtopics"].append(subtopic)
                i += 1
                continue

            i += 1

        result: list[dict[str, Any]] = []
        for section in sections:
            title = section.get("title", "").strip()
            if title:
                result.append({title: section.get("subtopics", [])})

        return result

    def _sanitize_topic_text(self, text: str) -> str:
        """Локальная очистка строкового заголовка темы/подтемы."""
        cleaned = self._clean_text(text)
        cleaned = re.sub(r'^[−–—•\*\-]+\s*', '', cleaned)
        cleaned = re.sub(r'^\d+(?:\.\d+)*[\.)]?\s*', '', cleaned)
        cleaned = re.sub(r'(?:\s+(?:\d+(?:[\.,]\d+)?|[-–—])){1,6}\s*$', '', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip(' ,.;:')
        return cleaned

    def _extract_section_text(
        self,
        text: str,
        start_patterns: list[str],
        end_pattern: str,
    ) -> str:
        """Извлекает фрагмент текста между заголовком секции и ее концом."""
        section_text = ""

        for pattern in start_patterns:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                section_text = text[match.start():]
                break

        if not section_text:
            return ""

        end_match = re.search(end_pattern, section_text, re.DOTALL | re.IGNORECASE | re.MULTILINE)
        if end_match:
            section_text = section_text[:end_match.start()]

        return section_text

    def _build_topic_title(self, kind: str, number: str, content: str) -> str:
        """Собирает читабельный заголовок раздела или темы."""
        normalized_content = self._clean_text(content)
        normalized_content = re.sub(r'^[−–—•\*\-]+\s*', '', normalized_content)
        # Убираем нумерацию вида "1.", "2)" в начале подпункта.
        normalized_content = re.sub(r'^\s*\d+(?:\.\d+)*[\.)]?\s+', '', normalized_content)
        # Убираем встроенные маркеры подпунктов, которые OCR склеивает в одну строку.
        normalized_content = re.sub(r'\b\d+\.\d+\.?\s*', ' ', normalized_content)
        normalized_content = re.sub(r'\b\d+\.(?=\s+[А-Яа-яA-Za-zЁё])', ' ', normalized_content)
        normalized_content = re.sub(r'(?<=\s)\d+(?=\s+[А-ЯA-ZЁ])', ' ', normalized_content)
        # Убираем хвостовые табличные значения типа "1 0,5" или "2 -".
        normalized_content = re.sub(
            r'(?:\s+(?:\d+(?:[\.,]\d+)?|[-–—])){1,6}\s*$',
            '',
            normalized_content,
        )
        normalized_content = re.sub(r'\b(?:Тема|Раздел)\s*$', '', normalized_content, flags=re.IGNORECASE)
        normalized_content = re.sub(r'(?i)тема$', '', normalized_content).strip()
        normalized_content = re.sub(r'\s{2,}', ' ', normalized_content)
        normalized_content = normalized_content.strip(' ,.;:')

        if re.fullmatch(r'[\d\s.]+', normalized_content):
            return ""  # Возвращаем пустую строку, если только цифры

        if normalized_content:
            return normalized_content

        return ""

    def _is_valid_topic(self, text: str) -> bool:
        """Проверяет, что строка похожа на раздел или тему, а не на служебный мусор."""
        if not text or len(text) < 3:
            return False
        
        if re.fullmatch(r'[\d\s.\-–—,;:()]+', text):
            return False

        text_lower = text.lower()

        blocked_fragments = [
            'номер раздела',
            'название и содержание',
            'содержание разделов и тем',
            'содержание дисциплины',
            'таблица',
            'лекции',
            'пз',
            'сз',
            'лр',
            'кп',
            'срс',
            'семестр',
            'итого',
            'час',
            'практическая подготовка',
        ]

        if len(text) > 220:
            return False

        if re.fullmatch(r'[\d\s.()\-–—,;:]+', text):
            return False

        for fragment in blocked_fragments:
            if fragment in text_lower:
                return False

        return True

    def _extract_list_items(self, text_block: str) -> list[str]:
        """Извлекает сырые элементы списка из текстового блока."""
        items: list[str] = []

        for raw_line in text_block.split("\n"):
            raw_line = raw_line.strip()
            if not raw_line:
                continue

            has_list_marker = bool(re.match(r'^[−–•\*\-\d+\.\)\s]+', raw_line))

            line = re.sub(r'^[−–•\*\-\d+\.\)\s]+', '', raw_line)
            line = line.strip(' ,.;:')

            
            line = re.split(r',\s*в\s+раздел\w*', line, maxsplit=1, flags=re.IGNORECASE)[0]
            line = line.strip(' ,.;:')

            quoted = re.findall(r'[«"]\s*([^»"]+?)\s*[»"]', line)
            candidate = quoted[0].strip() if quoted else line.strip('«»"')

            line = candidate.strip(' ,.;:«»"')

            if not line or len(line) <= 3:
                continue

            
            if line[0].islower() and not has_list_marker:
                continue

            items.append(line)

        return items

    def _clean_text(self, text: str) -> str:
        """Нормализует пробелы и переносы строк."""
        if not text:
            return text

        text = text.replace("\n", " ").replace("\r", "")
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _is_valid_discipline(self, text: str) -> bool:
        """Проверяет, что строка похожа на название дисциплины."""
        if not text or len(text) < 3:
            return False

        text_lower = text.lower()

        if "," in text:
            return False

        # Отсекаем фрагменты про школьный/общий образовательный уровень,
        # которые не являются вузовскими дисциплинами.
        if re.search(r'\b(школьн\w*|образован\w*|средн\w*\s+школ\w*)\b', text_lower):
            return False

        first_word = text_lower.split()[0] if text_lower.split() else ""
        if first_word in self.__bad_starts:
            return False

        return True

    def _clean_discipline_list(self, items: list[str]) -> list[str]:
        """Удаляет мусор и дубликаты из списка дисциплин."""
        cleaned: list[str] = []
        seen: set[str] = set()

        for item in items:
            item = item.strip()
            item = re.sub(r'^[−–•\*\-\s]+', '', item)
            item = item.strip(' ,.;:«»\'')

            if item and item[0].islower() and len(item.split()) > 2:
                continue

            if item and len(item) > 1:
                item = item[0].upper() + item[1:]

            if not item or len(item) < 3:
                continue

            if not self._is_valid_discipline(item):
                continue

            normalized = re.sub(r'\s+', '', item.lower())
            if normalized in seen:
                continue

            seen.add(normalized)
            cleaned.append(item)

        return cleaned
