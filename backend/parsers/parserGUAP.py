from typing import Any
import pymupdf
import os
import json
import re
from tqdm import tqdm


class ParserGUAP:
    """
    Парсер для РПД ГУАП.
    Автоматически обходит все вложенные папки.
    Извлекает название дисциплины и списки "до/после" из раздела 2.

    Итоговая структура данных:
    {
      "Название направления": {
        "Название дисциплины 1": {
          "previousDisciplines": ["дисциплина А", "дисциплина Б"],
          "nextDisciplines": ["дисциплина В", "дисциплина Г"],
          "topics": {}
        },
        "Название дисциплины 2": {
          "previousDisciplines": [...],
          "nextDisciplines": [...],
          "topics": {}
        }
      }
    }

    Пример использования:
        parser = ParserGUAP("путь/к/папке/с/pdf")
        data = parser.load_all_directions()
        parser.save_as_json("output.json")
    """

    def __init__(self, university_dir_name: str):
        """
        Инициализация парсера.

        Args:
            university_dir_name (str): Путь к корневой директории с PDF файлами.
                                      Может быть абсолютным или относительным.
        """
        self.__university_dir_name = university_dir_name
        self.__directions_of_study = {}  # {направление: {дисциплина: данные}}

        self.__title_marker = "РАБОЧАЯ ПРОГРАММА ДИСЦИПЛИНЫ"

        self.__stop_words = [
            "знания", "дисциплин", "—", "", "●", "•", "–", "-", "_", "",
            "выполнении плана", "подготовке выпускной", "преддипломной практики",
            "квалификационной работы", "дипломное проектирование", "вкр",
            "«культурология", "«основы", "«социология", "«философия",
            "имеют как", "самостоятельное значение", "материала данной дисциплины",
            "полученные при изучении", "ранее приобретенных", "при изучении следующих",
            "а также", "связанных с", "сетевые технологии", "защитой информации",
            "учебная практика", "производственная практика", "технологическая практика",
            "учебным планом", "не предусмотрено", "школьного курса", "курс физической культуры",
            "курс основы безопасности", "курс естествознания", "в средней школе",
            "так и могут использоваться при изучении других",
            "выпускной", "подготовке", "значение", "используются", "самостоятельное",
            "телекоммуникации", "базироваться", "может", "образования", "обучающимися",
            "приобретенных", "ранее", "среднего общего", "среднего профессионального", "",
            "данные", "информационная безопасность", "основы теории информации",
        ]

        self.__bad_starts = [
            "—", "«", "", "●", "•", "–", "-", "_", "", "",
            "в", "на", "при", "для", "и", "с", "со", "к", "по", "из", "за",
            "над", "под", "об", "от", "так", "также", "а", "но", "или"
        ]

    def load_all_directions(self) -> dict:
        """
        Автоматически загружает все направления из корневой директории.
        Обходит все вложенные папки.

        Returns:
            dict: Все загруженные данные в формате
                  {название_направления: {дисциплина: данные}}.
                  Пустой словарь, если директория не найдена, нет доступа
                  или не найдено ни одного PDF файла.

        Note:
            В процессе работы выводит прогресс-бар через tqdm.
            При ошибках доступа или проблемах с файлами выводит сообщения.
        """
        if not os.path.exists(self.__university_dir_name) or not os.path.isdir(self.__university_dir_name):
            print(f"Корневая директория не найдена: {self.__university_dir_name}")
            return {}

        try:
            items = os.listdir(self.__university_dir_name)
        except PermissionError:
            print(f"Нет доступа к директории: {self.__university_dir_name}")
            return {}

        for item in tqdm(items, desc="Обработка направлений", unit="папка", colour="green"):
            if os.path.isdir(os.path.join(self.__university_dir_name, item)):
                self._load_single_direction(item)

        if not self.__directions_of_study:
            print("В корневой директории не найдено ни одного направления с PDF файлами")

        return self.__directions_of_study

    def _load_single_direction(self, dir_of_direction: str) -> bool:
        """
        Загружает одно направление.

        Args:
            dir_of_direction (str): Имя папки с PDF файлами направления

        Returns:
            bool: True если загружена хотя бы одна дисциплина, иначе False

        Note:
            - Пропускает папки без PDF файлов
            - При ошибках доступа выводит сообщение и возвращает False
            - Использует вложенный прогресс-бар для отслеживания обработки файлов
        """
        directory = os.path.join(self.__university_dir_name, dir_of_direction)

        try:
            pdf_files = [f for f in os.listdir(directory)
                         if f.lower().endswith('.pdf') and os.path.isfile(os.path.join(directory, f))]
        except PermissionError:
            print(f"Нет доступа к папке: {dir_of_direction}")
            return False

        if not pdf_files:
            return False

        disciplines_dict = {}
        for file_name in tqdm(pdf_files, desc=f"  {dir_of_direction}", unit="файл", colour="green", leave=False):
            file_path = os.path.join(directory, file_name)
            discipline_data = self._read_discipline_from_file(file_path)
            if discipline_data:
                disciplines_dict.update(discipline_data)

        if disciplines_dict:
            self.__directions_of_study[dir_of_direction] = disciplines_dict
            return True
        return False

    def _read_discipline_from_file(self, file_path: str) -> dict[Any, Any] | None:
        """
        Прочитать данные дисциплины из PDF файла.

        Args:
            file_path (str): Полный путь к PDF файлу

        Returns:
            dict: Словарь {название_дисциплины: данные} или None в случае ошибки

        Note:
            - Извлекает текст со всех страниц PDF
            - При ошибках чтения или отсутствии названия выводит сообщение
            - Возвращает None, если не удалось извлечь название дисциплины
        """
        try:
            full_text = ""
            doc = pymupdf.open(file_path)

            for page_num in range(len(doc)):
                page = doc[page_num]
                page_text = page.get_text()
                if page_text:
                    full_text += page_text + "\n"

            doc.close()

            discipline_name = self._extract_discipline_name(full_text, file_path)
            if not discipline_name:
                print(f"Не удалось извлечь название из файла: {os.path.basename(file_path)}")
                return None

            prev_disciplines, next_disciplines = self._extract_disciplines_lists(full_text)

            discipline_data = {
                "previousDisciplines": prev_disciplines,
                "nextDisciplines": next_disciplines,
                "topics": {}
            }

            return {discipline_name: discipline_data}

        except Exception as e:
            print(f"Ошибка при обработке {os.path.basename(file_path)}: {e}")
            return None

    def _extract_discipline_name(self, text: str, file_path: str) -> str:
        """
        Извлекает название дисциплины из текста PDF.

        Сначала ищет по регулярным выражениям в тексте,
        при неудаче использует имя файла.

        Args:
            text (str): Текст, извлеченный из PDF
            file_path (str): Путь к файлу (для fallback)

        Returns:
            str: Название дисциплины или пустая строка, если не найдено
        """
        patterns = [
            r'РАБОЧАЯ ПРОГРАММА ДИСЦИПЛИНЫ\s*[«"]\s*([^»"]+)\s*[»"]',
            r'Дисциплина\s*[«"]\s*([^»"]+)\s*[»"]',
            r'Дисциплина\s+([А-Яа-яA-Za-z\s\-]+?)\s+входит',
            r'Дисциплина\s+([А-Яа-яA-Za-z\s\-]+?)\s+реализуется'
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name = self._clean_text(match.group(1))
                if name and len(name) > 3:
                    return name

        filename = os.path.splitext(os.path.basename(file_path))[0]
        filename = re.sub(r'^rpd_', '', filename)
        filename = re.sub(r'_\d+$', '', filename)
        return filename.replace('_', ' ').title()

    def _extract_disciplines_lists(self, text: str) -> tuple:
        """
        Извлекает списки дисциплин ДО и ПОСЛЕ из раздела 2.

        Args:
            text (str): Полный текст PDF

        Returns:
            tuple: (prev_list, next_list) - списки дисциплин
                   Могут быть пустыми, если раздел не найден
        """
        prev_list = []
        next_list = []

        section_pattern = r'2\.\s*Место дисциплины в структуре ОП(.*?)(?=\n\d+\.|\Z)'
        section_match = re.search(section_pattern, text, re.DOTALL | re.IGNORECASE)

        if not section_match:
            return prev_list, next_list

        section_text = section_match.group(1)

        prev_patterns = [
            r'базироваться на знаниях.*?при изучении следующих дисциплин:(.*?)(?=\n\n|\n[A-ZА-Я]|\Z)',
            r'может базироваться на знаниях.*?следующих дисциплин:(.*?)(?=\n\n|\n\d+\.|\Z)',
        ]

        for pattern in prev_patterns:
            prev_match = re.search(pattern, section_text, re.DOTALL | re.IGNORECASE)
            if prev_match:
                prev_block = prev_match.group(1)
                prev_list = self._extract_list_items(prev_block)
                if prev_list:
                    break

        next_patterns = [
            r'использоваться при изучении других дисциплин:(.*?)(?=\n\n|\n\d+\.|\Z)',
            r'могут использоваться при изучении других дисциплин:(.*?)(?=\n\n|\n\d+\.|\Z)',
            r'Знания.*?используются при изучении других дисциплин:(.*?)(?=\n\n|\n\d+\.|\Z)',
        ]

        for pattern in next_patterns:
            next_match = re.search(pattern, section_text, re.DOTALL | re.IGNORECASE)
            if next_match:
                next_block = next_match.group(1)
                next_list = self._extract_list_items(next_block)
                if next_list:
                    break

        prev_list = self._clean_discipline_list(prev_list)
        next_list = self._clean_discipline_list(next_list)
        prev_list, next_list = self._remove_intersection(prev_list, next_list)

        return prev_list, next_list

    def _extract_list_items(self, text_block: str) -> list:
        """
        Извлекает элементы списка из текстового блока.

        Args:
            text_block (str): Текстовый блок, содержащий список дисциплин

        Returns:
            list: Список сырых (неочищенных) названий дисциплин
        """
        items = []

        text_block = re.sub(r'^[−–•\*\-\s]+', '', text_block)

        quoted = re.findall(r'[«"]\s*([^»"]+?)\s*[»"]', text_block)
        items.extend([q.strip() for q in quoted if q.strip()])

        lines = text_block.split('\n')
        for line in lines:
            line = line.strip()
            line = re.sub(r'^[−–•\*\-\d+\.\s]+', '', line)
            line = line.strip(' ,.;:«»"')

            if line and len(line) > 3:
                if ',' in line and not re.search(r'\d', line):
                    parts = [p.strip(' «»"') for p in line.split(',')]
                    items.extend([p for p in parts if p])
                else:
                    items.append(line)

        return items

    def _clean_text(self, text: str) -> str:
        """
        Очищает текст от лишних пробелов и переносов строк.

        Args:
            text (str): Исходный текст

        Returns:
            str: Очищенный текст с одинарными пробелами
        """
        if not text:
            return text

        text = text.replace('\n', ' ').replace('\r', '')
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def _is_valid_discipline(self, text: str) -> bool:
        """
        Проверяет, является ли текст названием дисциплины.

        Args:
            text (str): Текст для проверки

        Returns:
            bool: True если текст похож на название дисциплины
        """
        if not text or len(text) < 3:
            return False

        text_lower = text.lower()

        for word in self.__stop_words:
            if word.lower() in text_lower:
                return False

        first_word = text_lower.split()[0] if text_lower.split() else ""
        if first_word in self.__bad_starts:
            return False

        return True

    def _clean_discipline_list(self, items: list) -> list:
        """
        Очищает список дисциплин от мусора и дубликатов.

        Args:
            items (list): Список "сырых" названий

        Returns:
            list: Очищенный список уникальных названий
        """
        cleaned = []
        seen = set()

        for item in items:
            item = item.strip()
            item = re.sub(r'^[−–•\*\-\s]+', '', item)
            item = item.strip(' ,.;:«»"\'')

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

        return sorted(cleaned)

    def _remove_intersection(self, prev_list: list, next_list: list) -> tuple:
        """
        Удаляет пересечения между списками previous и next.

        Args:
            prev_list (list): Список дисциплин ДО
            next_list (list): Список дисциплин ПОСЛЕ

        Returns:
            tuple: (обновленный prev_list, обновленный next_list)
                  без общих элементов
        """
        if not prev_list or not next_list:
            return prev_list, next_list

        prev_set = set(prev_list)
        next_set = set(next_list)
        common = prev_set & next_set

        if common:
            prev_list = [x for x in prev_list if x not in common]
            next_list = [x for x in next_list if x not in common]

        return prev_list, next_list

    def get_direction(self, direction: str) -> dict:
        """
        Получить данные конкретного направления.

        Args:
            direction (str): Название направления

        Returns:
            dict: Данные направления {дисциплина: данные}
                  Пустой словарь, если направление не найдено
        """
        if direction in self.__directions_of_study:
            return self.__directions_of_study[direction]
        return {}

    def get_all_directions(self) -> dict:
        """
        Получить все загруженные данные.

        Returns:
            dict: Все загруженные направления и дисциплины
        """
        return self.__directions_of_study

    def save_as_json(self, file_name: str) -> bool:
        """
        Сохранить все загруженные данные в JSON файл.

        Args:
            file_name (str): Имя файла для сохранения

        Returns:
            bool: True если сохранение успешно, иначе False

        Note:
            Файл сохраняется с отступами (indent=2) для читаемости.
            При ошибках сохранения выводит сообщение.
        """
        try:
            with open(file_name, 'w', encoding='utf-8') as f:
                json.dump(self.__directions_of_study, f, ensure_ascii=False, indent=2)
            print(f"Данные сохранены в {file_name}")
            return True
        except Exception as e:
            print(f"Ошибка при сохранении JSON: {e}")
            return False
