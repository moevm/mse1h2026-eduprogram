import fitz #MyPyPDF
import os
import json
import re


class ParserMPU:
    """
    Парсер для МПУ (Московский Политехнический Университет).
    Обходит все файлы в папке с дисциплинами.
    Извлекает название дисциплины, последующие дисциплины (nextDisciplines) и темы с подтемами.
    """

    def __init__(self, universityDirName: str):
        self.__universityDirName = universityDirName
        self.__directionsOfStudy = {}

        self.__titleOfDocument = "РАБОЧАЯ ПРОГРАММА ДИСЦИПЛИНЫ"
        self.__disciplineNameEndMarker = "Направление подготовки"

        self.__nextDisciplinesMarkers = [
            "дисциплинами и практиками ОПОП",
            "дисциплинами и практиками ООП"
        ]

        self.__contentStartMarker = "Содержание дисциплины"
        self.__contentEndPatterns = [
            "4 Учебно-методическое",
            "4. Учебно-методическое",
            "4."
        ]

    def loadDirectionOfStudy(self, dirOfDirection: str) -> bool:
        """Загружает все дисциплины из указанной папки направления."""
        if dirOfDirection in self.__directionsOfStudy:
            return True

        directory = os.path.join(self.__universityDirName, "МПУ", dirOfDirection)
        if not os.path.exists(directory) or not os.path.isdir(directory):
            print(f"Папка не найдена: {directory}")
            return False

        listOfDisciplines = []
        for fileName in os.listdir(directory):
            if fileName.lower().endswith('.pdf'):
                filePath = os.path.join(directory, fileName)
                print(f"Файл: {fileName}")
                discipline, arguments = self._read_discipline_file(filePath)
                if discipline and arguments:
                    listOfDisciplines.append({discipline: arguments})
                    if arguments.get("nextDisciplines"):
                        print(f"  -> Найдены дисциплины: {arguments['nextDisciplines']}")

        self.__directionsOfStudy[dirOfDirection] = listOfDisciplines
        print(f"Загружено дисциплин: {len(listOfDisciplines)}")
        return True

    def getDirection(self, direction: str) -> dict:
        """Возвращает данные по конкретному направлению."""
        return self.__directionsOfStudy.get(direction, {})

    def getAllDirections(self) -> dict:
        """Возвращает все загруженные направления."""
        return self.__directionsOfStudy

    def saveAsJson(self, fileName: str) -> bool:
        """Сохраняет результат в JSON-файл."""
        try:
            with open(fileName, 'w', encoding='utf-8') as f:
                json.dump(self.__directionsOfStudy, f, ensure_ascii=False, indent=4)
            print(f"Данные сохранены в {fileName}")
            return True
        except Exception as e:
            print(f"Ошибка сохранения: {e}")
            return False

    @staticmethod
    def _clean_text(text: str) -> str:
        """Убирает лишние пробелы."""
        return re.sub(r'\s+', ' ', text).strip()

    @staticmethod
    def _check_text(text: str) -> bool:
        """Проверяет, что текст содержит буквы и что он достаточной длины."""
        if not text or len(text) < 3:
            return False
        return any(c.isalpha() for c in text)

    def _extract_text_from_pdf(self, filePath: str) -> str:
        """Извлекает текст из PDF-файла."""
        try:
            doc = fitz.open(filePath)
            text = ""
            for page in doc:
                text += page.get_text()
                text += "\n"
            doc.close()
            return text
        except Exception as e:
            print(f"Ошибка чтения Pdf: {e}")
            return ""

    def _extract_discipline_name(self, full_text: str) -> str:
        """Извлекает название дисциплины."""
        title_pos = full_text.find(self.__titleOfDocument)
        if title_pos == -1:
            return ""

        after_title = full_text[title_pos + len(self.__titleOfDocument):]
        dir_pos = after_title.find(self.__disciplineNameEndMarker)
        if dir_pos != -1:
            name = after_title[:dir_pos].strip()
        else:
            lines = after_title.split('\n')
            name = next((line.strip() for line in lines if line.strip()), "")

        name = name.strip('«»"')
        return self._clean_text(name)

    def _extract_next_disciplines(self, full_text: str) -> list:
        """Извлекает список последующих дисциплин."""
        next_disciplines = []

        marker_pos = -1
        used_marker = ""
        for marker in self.__nextDisciplinesMarkers:
            pos = full_text.find(marker)
            if pos != -1:
                marker_pos = pos
                used_marker = marker
                break

        if marker_pos == -1:
            return next_disciplines

        after_marker = full_text[marker_pos + len(used_marker):]
        colon_pos = after_marker.find(':')
        if colon_pos == -1:
            return next_disciplines

        after_colon = after_marker[colon_pos + 1:]

        section_3_pos = after_colon.find("\n3.")
        if section_3_pos == -1:
            section_3_pos = after_colon.find("\n3 ")
        if section_3_pos == -1:
            section_3_pos = len(after_colon)

        block = after_colon[:section_3_pos]

        lines = block.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line and (line[0] in '•-*●·' or line.startswith('- ') or line.startswith('* ')):
                clean = re.sub(r'^[•\-*\●·\s]+', '', line).strip()
                clean = clean.rstrip(';')
                if self._check_text(clean):
                    next_disciplines.append(clean)
            elif ';' in line and len(line) > 10:
                parts = line.split(';')
                for part in parts:
                    part = part.strip()
                    if self._check_text(part):
                        next_disciplines.append(part)

        return next_disciplines

    def _split_into_sentences(self, text: str) -> list:
        """Разбивает текст на предложения (пока просто по точкам)."""
        if not text:
            return []

        text = text.replace('\n', ' ')

        text = re.sub(r'т\.\s*д\.', 'ТД', text, flags=re.IGNORECASE)
        text = re.sub(r'т\.\s*п\.', 'ТП', text, flags=re.IGNORECASE)
        text = re.sub(r'и\.\s*т\.\s*д\.', 'ИТД', text, flags=re.IGNORECASE)
        text = re.sub(r'и\.\s*т\.\s*п\.', 'ИТП', text, flags=re.IGNORECASE)

        sentences = re.split(r'\.\s+', text)

        sentences = [s.replace('ТД', 'т.д.').replace('ТП', 'т.п.').replace('ИТД', 'и т.д.').replace('ИТП', 'и т.п.') for s in sentences]

        result = []
        for sent in sentences:
            sent = sent.strip()
            sent = re.sub(r'^\d+\.?\d*\s*', '', sent)
            sent = self._clean_text(sent)
            if self._check_text(sent) and len(sent) > 5:
                result.append(sent)

        return result

    def _extract_topics(self, full_text: str) -> dict:
        """Извлекает темы и подтемы из раздела «Содержание дисциплины»."""
        topics = {}

        content_pos = full_text.find("3.3 Содержание дисциплины")
        if content_pos == -1:
            content_pos = full_text.find("3.3 Содержание")
        if content_pos == -1:
            content_pos = full_text.find(self.__contentStartMarker)
        if content_pos == -1:
            return topics

        end_pos = None
        for marker in self.__contentEndPatterns:
            pos = full_text.find(marker, content_pos)
            if pos != -1:
                end_pos = pos
                break
        if end_pos is None:
            end_pos = content_pos + 10000

        content_text = full_text[content_pos:end_pos]

        topic_pattern = re.compile(
            r'(?s)(?:Раздел|Тема)\s*(\d+)[\.:\-]?\s*(.*?)(?=(?:Раздел|Тема)\s*\d+|\Z)',
            re.IGNORECASE
        )

        for match in topic_pattern.finditer(content_text):
            topic_content = match.group(2).strip()
            sentences = self._split_into_sentences(topic_content)
            if sentences:
                topic_title = sentences[0]
                subtopics = sentences[1:] if len(sentences) > 1 else []
                if subtopics:
                    topics[topic_title] = subtopics

        return topics

    def _read_discipline_file(self, filePath: str) -> tuple:
        """Читает файл дисциплины, возвращает (название, словарь с данными)."""
        try:
            full_text = self._extract_text_from_pdf(filePath)
            if not full_text:
                return None, None

            if self.__titleOfDocument not in full_text:
                return None, None

            name = self._extract_discipline_name(full_text)
            if not name:
                name = os.path.basename(filePath).replace('.pdf', '')
                name = re.sub(r'[B0-9._]+', '', name)
                name = name.replace('_', ' ').strip()

            next_disc = self._extract_next_disciplines(full_text)
            topics = self._extract_topics(full_text)

            return name, {
                "previousDisciplines": [],
                "nextDisciplines": next_disc,
                "topics": topics
            }
        except Exception as e:
            print(f"Ошибка парсинга {os.path.basename(filePath)}: {e}")
            return None, None


if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    print("Парсер МПУ")
    print("-" * 30)

    parser = ParserMPU(current_dir)
    if parser.loadDirectionOfStudy("Системная и программная инженерия"):
        parser.saveAsJson("mpu_disciplines.json")
    else:
        print("Ошибка загрузки")