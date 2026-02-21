import fitz
import os
import json
import re


class ParserSpbPU:
    def __init__(self, universityDirName: str):
        self.__universityDirName = universityDirName
        self.__directionsOfStudy = {}  # временное решение, потом все будет храниться в БД
        self.__textForPreviousDisciplines = "Изучение дисциплины базируется на результатах освоения " \
                                            "следующих дисциплин: \n"
        self.__titleOfDocument = "РАБОЧАЯ ПРОГРАММА ДИСЦИПЛИНЫ (МОДУЛЯ) \n"
        self.__textForEducationalUnits = "4.2. Содержание разделов и результаты изучения дисциплины \n" \
                                         "Раздел дисциплины Содержание \n"
        self.__endTextForEducationalUnits = "5. Образовательные технологии"

    def loadDirectionOfStudy(self, dirOfDirection: str) -> bool:
        """Метод загрузки нового направления"""
        if dirOfDirection in self.__directionsOfStudy:
            return True

        directory = os.path.join(self.__universityDirName, dirOfDirection)
        if not os.path.exists(directory) or not os.path.isdir(directory):
            print(directory)
            return False

        listOfDisciplines = []
        for fileNameDiscipline in os.listdir(directory):
            filePathDiscipline = os.path.join(directory, fileNameDiscipline)
            if os.path.isfile(filePathDiscipline):
                discipline, arguments = self.readTextFromFileDiscipline(filePathDiscipline)
                if discipline and arguments:
                    listOfDisciplines.append({discipline: arguments})
        self.__directionsOfStudy[dirOfDirection] = listOfDisciplines
        return True

    def getDirection(self, direction: str) -> dict:
        """Метод получения направления"""
        if direction in self.__directionsOfStudy:
            return self.__directionsOfStudy[direction]
        return {}

    def getAllDirections(self) -> dict:
        """Получить все направления"""
        return self.__directionsOfStudy

    def saveAsJson(self, fileName: str) -> bool:
        """СОхранить в json файл"""
        try:
            with open(fileName, 'w', encoding='utf-8') as file:
                json.dump(self.__directionsOfStudy, file, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            return False

    @staticmethod
    def __refactorText(text: str) -> str:
        """Метод обработки текста для учебных единиц"""
        text = re.sub(r'\n(?=[А-ЯA-Z])', '$', text)
        text = re.sub(r'\d+\.\d+', '', text)
        text = re.sub(r'Темы:', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        text = re.sub(r'\d+\)\s*(\S+)', '', text)
        text = text.replace(". ", "$").replace(";", "$")
        text = text.replace(".", "")
        return text

    @staticmethod
    def __checkText(text: str) -> bool:
        """Проверка корретной информации"""
        flag = False
        for el in text:
            if el.isalpha():
                flag = True
                break
        return flag and len(text.strip()) > 2

    def readTextFromFileDiscipline(self, filePathDiscipline: str) -> tuple:
        """Прочитать учебный план направления из файла и вернуть информацию"""
        try:
            fullText = ""
            document = fitz.open(filePathDiscipline)
            linesBoldFont = []

            for page_num in range(len(document)):
                page = document[page_num]

                textPage = page.get_text("dict")
                for block in textPage.get("blocks", []):
                    if "lines" in block:
                        for line in block["lines"]:
                            for span in line["spans"]:
                                fullText += span["text"] + " "
                                if span["flags"] == 20:
                                    linesBoldFont.append(span["text"].strip())
                        fullText += "\n"

                fullText += "\n"

            document.close()
            if self.__titleOfDocument not in fullText:
                print(f"{filePathDiscipline}: this is not discipline!")
                return None, None

            indexOfNameDiscipline = fullText.find(self.__titleOfDocument)
            disciplineName = fullText[indexOfNameDiscipline + len(self.__titleOfDocument):]
            disciplineName = disciplineName[1:disciplineName.find("»")].strip()

            indexOfPreviousDisciplines = fullText.find(self.__textForPreviousDisciplines)
            listOfPreviousDisciplines = []
            if indexOfPreviousDisciplines != -1:
                subText = fullText[indexOfPreviousDisciplines + len(self.__textForPreviousDisciplines):]
                subText = subText[:subText.find("•")]
                for discipline in subText.split("\n"):
                    if self.__checkText(discipline):
                        listOfPreviousDisciplines.append(discipline.strip())

            resultForAllTopics = {}
            indexOfEducationalUnits = fullText.find(self.__textForEducationalUnits)
            subText = fullText[indexOfEducationalUnits + len(self.__textForEducationalUnits):]
            subText = subText[:subText.find(self.__endTextForEducationalUnits)]
            lines = subText.split("\n")
            nameTopic = ""
            listOfEducationalUnits = []
            textOfEducationalUnits = ""
            flagTopic = False
            flagUnits = False
            for i, line in enumerate(lines):
                if line.strip() in linesBoldFont or i == len(lines) - 1:
                    if (flagTopic and flagUnits) or i == len(lines) - 1:
                        textOfEducationalUnits = self.__refactorText(textOfEducationalUnits)
                        for unit in textOfEducationalUnits.split("$"):
                            if self.__checkText(unit):
                                listOfEducationalUnits.append(unit.strip())
                        if nameTopic and listOfEducationalUnits and nameTopic[0].isdigit():
                            nameTopic = nameTopic[nameTopic.find(". ") + 2:]
                            nameTopic = re.sub(r'\d+\.', '', nameTopic)
                            resultForAllTopics[nameTopic.strip()] = listOfEducationalUnits
                    if flagUnits:
                        nameTopic = ""
                        textOfEducationalUnits = ""
                        listOfEducationalUnits = []
                        flagUnits = False
                    if line and line[0].isdigit():
                        nameTopic = ""
                    nameTopic += line
                    flagTopic = True
                else:
                    textOfEducationalUnits += line + "\n"
                    flagUnits = True

            return disciplineName, {
                "previousDisciplines": listOfPreviousDisciplines,
                "topics": resultForAllTopics
            }

        except Exception as e:
            print(f"{filePathDiscipline}: Error: {e}")
            return None, None
