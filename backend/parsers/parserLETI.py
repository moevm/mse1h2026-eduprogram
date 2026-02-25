import fitz
import os
import json
import re


class ParserLETI:
    """
    Парсер для извлечения данных из рабочих программ дисциплин СПбГЭТУ "ЛЭТИ"
    Извлекает: название дисциплины, предшествующие дисциплины, темы и их содержание
    """

    def __init__(self, universityDirName: str):

        self.universityDirName = universityDirName
        self.directionsOfStudy = {}  # Словарь для хранения всех дисциплин по направлениям

        # Маркеры для поиска в тексте PDF
        self.textForPreviousSubject = "Дисциплина изучается на основе ранее освоенных дисциплин учебного плана:"
        self.endTextForPreviousSubject = "и обеспечивает"
        self.textForSubjectTopics = "4.1.2 Содержание"  # Раздел с темами
        self.endText = "4.2 Перечень лабораторных работ"  # Конец раздела с темами
        self.textWithNameSubject = "РАБОЧАЯ ПРОГРАММА дисциплины"  # Маркер названия дисциплины

    def getTextFromDict(self, textDict):
        """
        Извлекает текст из словаря, полученного от PyMuPDF (fitz)
        Args:
            textDict: словарь с структурой страницы PDF
        Returns:
            строка с текстом страницы
        """
        result = []
        # Проходим по блокам страницы
        for block in textDict.get("blocks", []):
            if block.get("type") == 0:  # 0 - текстовый блок
                for line in block.get("lines", []):
                    # Склеиваем текст из всех span'ов в линии
                    lineText = "".join(span.get("text", "") for span in line.get("spans", []))
                    result.append(lineText)
        return "\n".join(result)

    def getDirection(self, direction: str) -> dict:
        """Метод получения направления"""
        if direction in self.__directionsOfStudy:
            return self.__directionsOfStudy[direction]
        return {}

    def getAllDirections(self) -> dict:
        """Получить все направления"""
        return self.__directionsOfStudy

    def readPdf(self, pdfPath):
        """
        Основной метод обработки одного PDF файла
        Args:
            pdfPath: путь к PDF файлу
        Returns:
            словарь с данными дисциплины или None если не удалось распарсить
        """
        fullText = ""
        subjectName = ""
        listPreviousSubject = []

        doc = fitz.open(pdfPath)

        # Извлекаем текст со всех страниц
        for page in doc:
            textDict = page.get_text("dict")
            pageText = self.getTextFromDict(textDict)
            fullText += pageText + "\n"

        doc.close()

        # Очищаем текст от спецсимволов PDF
        fullText = self.cleanPdfText(fullText)

        # Ищем название дисциплины
        if fullText.find(self.textWithNameSubject) != -1:
            startIdx = fullText.find(self.textWithNameSubject) + len(self.textWithNameSubject) + 2
            endIdx = fullText.find("»", startIdx)
            if endIdx != -1:
                subjectName = fullText[startIdx:endIdx]
                subjectName = self.normalizeSpaces(subjectName).capitalize()

        # Ищем предшествующие дисциплины
        if fullText.find(self.textForPreviousSubject) != -1:
            startIdx = fullText.find(self.textForPreviousSubject) + len(self.textForPreviousSubject)
            endIdx = fullText.find(self.endTextForPreviousSubject, startIdx)
            if endIdx == -1:
                endIdx = len(fullText)

            subjectBlock = fullText[startIdx:endIdx]
            subjectBlock = self.normalizeSpaces(subjectBlock)

            # Регулярка: находим все названия в кавычках «…»
            # «(.*?)» - захват всего что между кавычками
            listPreviousSubject = re.findall(r'«(.*?)»', subjectBlock)
            listPreviousSubject = [self.normalizeSpaces(s) for s in listPreviousSubject]

        # Извлекаем блок с темами
        textTopics = ""
        if self.textForSubjectTopics in fullText:
            startIdx = fullText.find(self.textForSubjectTopics) + len(self.textForSubjectTopics)
            endIdx = fullText.find(self.endText)  # Ищем до начала лабораторных работ
            textTopics = fullText[startIdx:endIdx].strip()
            # Удаляем "Тема 1", "Тема 1.", "Тема 1.1" и т.д. в любом регистре
            textTopics = re.sub(r'(?i)тема\s*\d+(\.\d+)*\.?\s*', '', textTopics)
            # Также удаляем просто "Тема" если осталось
            textTopics = re.sub(r'(?i)тема\s*', '', textTopics)

        # Разбиваем на отдельные темы по номерам
        themes = self.splitByNumberedTopics(self.removeTableHeaders(textTopics))
        themes = [self.cleanPdfSpaces(s) for s in themes]

        # Парсим каждую тему
        parsed = []
        for topic in themes:
            parsed.append(self.parseTopicBlock(topic))

        filteredThemes = [
            theme for theme in parsed
            if not list(theme.keys())[0].startswith(("Введение", "Заключение"))
        ]

        filtered = self.cleanThemeItems(filteredThemes)

        resultJson = {
            subjectName: {
                "previousDisciplines": listPreviousSubject,
                "topics": filtered
            }
        }

        if not themes:
            return None

        return resultJson

    def start(self):
        """
        Запуск парсера - обрабатывает все PDF во всех директориях
        """
        directories = self.getDirectories()

        for directoryName in directories:
            targetDir = os.path.join(self.universityDirName, directoryName)
            self.directionsOfStudy[directoryName] = []  # Инициализируем список для направления

            if not os.path.exists(targetDir) or not os.path.isdir(targetDir):
                print(f"Директория не существует: {targetDir}")
                continue

            # Находим все PDF файлы в директории
            pdfFiles = [
                f for f in os.listdir(targetDir)
                if f.lower().endswith(".pdf") and os.path.isfile(os.path.join(targetDir, f))
            ]
            if not pdfFiles:
                print(f"PDF файлы не найдены в директории {directoryName}")
                continue

            print(f"\nНайдено {len(pdfFiles)} PDF файлов в {directoryName}:")
            for pdfFile in pdfFiles:
                pdfPath = os.path.join(targetDir, pdfFile)

                try:
                    pdfData = self.readPdf(pdfPath)
                    if pdfData:
                        self.directionsOfStudy[directoryName].append(pdfData)
                except Exception as e:
                    print(f"Ошибка при обработке {pdfFile}: {e}")

        # Сохраняем результат в JSON
        outputFile = os.path.join(self.universityDirName, "all_disciplines.json")
        with open(outputFile, "w", encoding="utf-8") as f:
            json.dump(self.directionsOfStudy, f, ensure_ascii=False, indent=4)

        print(f"Данные всех направлений сохранены в {outputFile}")

    @staticmethod
    def splitByNumberedTopics(text: str):
        """
        Разбивает текст на блоки по номерам (1, 2, 3...)
        Args:
            text: текст с нумерованными темами
        Returns:
            список блоков тем
        """
        topics = []
        currentNum = 1

        while True:
            currentMarker = f"{currentNum} "  # "1 ", "2 ", "3 " и т.д.
            nextMarker = f"{currentNum + 1} "

            startIdx = text.find(currentMarker)
            if startIdx == -1:
                break  # Нет даже первого номера конец

            startIdx += len(currentMarker)


            endIdx = text.find(nextMarker)

            if endIdx == -1:
                # Это последний блок — берём до конца
                block = text[startIdx:].strip()
                topics.append(block)
                break

            # Берём текст до следующего номера
            block = text[startIdx:endIdx].strip()
            topics.append(block)

            currentNum += 1

        return topics

    @staticmethod
    def parseTopicBlock(block: str):
        """
        Парсит блок одной темы на название и содержание
        Args:
            block: текст блока темы
        Returns:
            словарь {название_темы: [список_предложений]}
        """
        # Убираем ведущий номер в начале
        block = re.sub(r"^\s*\d+\s*", "", block)  # регулярка: пробелы, цифры, пробелы

        # Убираем слово "Тема" с номером
        # (?i) - игнорирование регистра, ^ - начало строки, \d+ - цифры, \.? - точка опционально
        block = re.sub(r"(?i)^тема\s*\d+\.?\s*", "", block).strip()

        # Найти первую точку с пробелом (конец названия темы)
        firstDotIdx = block.find('. ')
        if firstDotIdx == -1:
            # Точек нет, весь блок — название, содержимого нет
            return {block.strip(): []}

        # Название = всё до первой точки
        title = block[:firstDotIdx].strip()

        # Содержание = всё после первой точки, разбиваем по точкам
        contentText = block[firstDotIdx + 1:].strip()

        # Разбиваем по точкам с пробелом, убираем пустые
        sentences = [s.strip() for s in contentText.split('. ') if s.strip()]

        return {title: sentences}

    def getDirectories(self):
        """Получить список всех директорий в папке"""
        directories = []

        if not os.path.exists(self.universityDirName):
            print(f"Папка {self.universityDirName} не существует")
            return directories

        for item in os.listdir(self.universityDirName):
            itemPath = os.path.join(self.universityDirName, item)
            if os.path.isdir(itemPath):
                directories.append(item)

        return directories

    @staticmethod
    def normalizeSpaces(s: str) -> str:
        """
        Заменяет все пробельные символы на один пробел
        """
        # \s+ - один или более пробельных символов (пробел, таб, перенос строки)
        return re.sub(r'\s+', ' ', s).replace("\xad", " ").replace(" \n", "").strip()

    @staticmethod
    def cleanPdfSpaces(text: str) -> str:
        """
        Преобразует все спец-пробелы PDF в обычные пробелы
        """
        # Список юникод-символов пробелов, которые часто встречаются в PDF
        pdfSpaces = [
            "\u00A0",  # неразрывный пробел
            "\u2000", "\u2001", "\u2002", "\u2003", "\u2004",  # пробелы разной ширины
            "\u2005", "\u2006", "\u2007", "\u2008", "\u2009", "\u200A",
            "\u202F", "\u205F", "\u3000",  # узкие и широкие пробелы
            "\xad", "\u00AD",  # мягкий перенос (soft hyphen)
            "\u200B"  # zero-width space
        ]
        for space in pdfSpaces:
            text = text.replace(space, " ")

        # Заменяем множественные пробелы на один
        text = re.sub(r"[ ]+", " ", text)
        return text.strip()

    @staticmethod
    def cleanPdfText(s: str) -> str:
        """
        Комплексная очистка текста от PDF-спецсимволов
        """
        pdfSpaces = [
            "\u00A0", "\u2000", "\u2001", "\u2002", "\u2003", "\u2004",
            "\u2005", "\u2006", "\u2007", "\u2008", "\u2009", "\u200A",
            "\u202F", "\u205F", "\u3000", "\u00AD", "\u200B"
        ]

        # Удаляем мягкий перенос с переносом строки
        s = re.sub(r'\xad\n', '', s)
        s = s.replace("\u00AD", "")

        # Удаляем управляющие символы (диапазоны юникода)
        s = re.sub(r'[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f\u00ad]', '', s)

        # Заменяем спец-пробелы на обычные
        for space in pdfSpaces:
            s = s.replace(space, " ")

        # Склеиваем слова, разорванные дефисом с переносом строки
        s = re.sub(r"-\n", "", s)

        # Заменяем одиночные переносы строк на пробелы
        # (?<!\n)\n(?!\n) - перенос строки, у которого нет соседей-переносов
        s = re.sub(r"(?<!\n)\n(?!\n)", " ", s)

        # Нормализуем пробелы
        s = re.sub(r"\s+", " ", s)
        return s.strip()



    @staticmethod
    def removeTableHeaders(text: str) -> str:
        """
        Удаляет заголовки таблиц из текста
        Регулярка: цифры, пробелы, №, п/п, затем до 60 любых символов, затем Содержание
        """
        pattern = r"\d+\s*№\s*п/п[\s\S]{0,60}?Содержание"
        return re.sub(pattern, "", text)

    def cleanThemeItems(self, themes):
        """
        Дополнительная очистка тем от мусора
        Args:
            themes: список тем с содержанием
        Returns:
            очищенный список тем
        """
        cleaned = []

        # Слова, которые нужно удалить (в любом регистре)
        forbiddenWords = r"(семинар|тема|темы)"

        for theme in themes:
            newTheme = {}
            for title, content in theme.items():
                newContent = []
                for line in content:

                    # Удаляем запрещённые слова
                    line = re.sub(forbiddenWords, "", line, flags=re.IGNORECASE)


                    # \([^)]*\) - открывающая скобка, любые символы кроме ), закрывающая скобка
                    line = re.sub(r"\([^)]*\)", "", line)

                    # Удаляем строки короче 3 символов
                    if len(line.strip()) < 3:
                        continue

                    # Удаляем строки, состоящие только из цифр и/или точек
                    # [.\d]+ - один или более символов из набора (точка, цифра)
                    if re.fullmatch(r"[.\d]+", line.strip()):
                        continue

                    # Удаляем нумерацию в начале строки
                    # ^\s*\d+[\.\)]*\s* - пробелы, цифры, точка или скобка, пробелы
                    line = re.sub(r"^\s*\d+[\.\)]*\s*", "", line)

                    # Удаляем знаки препинания (иногда остаются висячими)
                    line = line.replace(":", "").replace(";", "").replace("+", "")

                    # Финальная нормализация
                    line = self.normalizeSpaces(line).strip()
                    if not line or len(line.strip()) < 3:
                        continue

                    newContent.append(line)

                newTheme[title] = newContent
                cleaned.append(newTheme)

        return cleaned


if __name__ == "__main__":
    
    parser = ParserLETI(os.path.join(os.path.expanduser("~/Desktop"), "СПбГЭТУ ЛЭТИ"))
    parser.start()