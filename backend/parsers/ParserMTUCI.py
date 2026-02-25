import fitz
import os
import json
import re


class ParserMTUCI:
    def __init__(self, universityDirName: str):
        self.__universityDirName = universityDirName
        self.__directionsOfStudy = {}

        self.__titleOfDocument = ["Рабочая программа дисциплины  ", "Рабочая программа элективной дисциплины  "]
        self.__textForPreviousDisciplines = ["формируются у  обучающихся в результате изучения дисциплины ",
                                             "Для освоения дисциплины необходимы навыки, приобретенные в результате "
                                             "изучения  таких дисциплин как"]
        self.__textForEducationalUnits = ["индикаторов   компетенций  ", "индикаторов  компетенций  ",
                                          "индикаторов  компетенции  ", "индикаторов   компетенции  ",
                                          "индикаторов  компетенций"]
        self.__endTextForTopics = ['Лекция', 'Лабораторная работа', 'Практическая работа', '№ п/п', 'Практическое занятие']
        self.__endTextForEducationalUnits = ('5. Учебно-методическое')

    def loadDirectionOfStudy(self, dirOfDirection: str) -> bool:
        if dirOfDirection in self.__directionsOfStudy:
            return True

        directory = os.path.join(self.__universityDirName, dirOfDirection)
        if not os.path.exists(directory) or not os.path.isdir(directory):
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
        if direction in self.__directionsOfStudy:
            return self.__directionsOfStudy[direction]
        return {}

    def getAllDirections(self) -> dict:
        return self.__directionsOfStudy

    def saveAsJson(self, fileName: str) -> bool:
        try:
            with open(fileName, 'w', encoding='utf-8') as file:
                json.dump(self.__directionsOfStudy, file, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            return False

    @staticmethod
    def __refactorText(text: str) -> str:
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
        flag = False
        for el in text:
            if el.isalpha():
                flag = True
                break
        return flag and len(text.strip()) > 2

    @staticmethod
    def __cut_by_words(text: str, words: list[str]) -> str:
        positions = [
            text.find(word)
            for word in words
            if text.find(word) != -1
        ]
        if not positions:
            return text
        return text[:min(positions)].strip()

    def readTextFromFileDiscipline(self, filePathDiscipline: str) -> tuple:
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

            disciplineName = ''
            for i in range(len(self.__titleOfDocument)):
                indexOfNameDiscipline = fullText.find(self.__titleOfDocument[i])
                if indexOfNameDiscipline != -1:
                    disciplineName = fullText[indexOfNameDiscipline + len(self.__titleOfDocument[i]):]
                    disciplineName = disciplineName[1:disciplineName.find("Направление подготовки")].strip()
                    if len(disciplineName) > 200:
                        disciplineName = disciplineName.split("\n")[0]
                    disciplineName = re.sub(r"\s+", " ", disciplineName)
                    disciplineName = disciplineName.lower()

            if disciplineName == '':
                print(f"{filePathDiscipline}: this is not discipline!")
                return None, None

            listOfPreviousDisciplines = []
            for i in range(len(self.__textForPreviousDisciplines)):
                indexOfPreviousDisciplines = fullText.find(self.__textForPreviousDisciplines[i])
                if indexOfPreviousDisciplines != -1:
                    subText = fullText[indexOfPreviousDisciplines + len(self.__textForPreviousDisciplines[i]):]
                    subText = subText[:subText.find(".")]
                    for discipline in subText.split(", "):
                        if self.__checkText(discipline):
                            listOfPreviousDisciplines.append(discipline.strip(" ««»").replace("  ", " "))
                    break

            resultForAllTopics = {}
            for i in range(len(self.__textForEducationalUnits)):
                indexOfEducationalUnits = fullText.find(self.__textForEducationalUnits[i])
                if indexOfEducationalUnits != -1:
                    subText = fullText[indexOfEducationalUnits + len(self.__textForEducationalUnits[i]):]
                    subText = re.sub(r"\s+", " ", subText)
                    subText = subText[:subText.find(self.__endTextForEducationalUnits)]
                    parts = re.split(r'(\d+\.\s*Раздел\s*\d+\.)', subText)

                    sections = {}
                    for i in range(1, len(parts), 2):
                        section_header = parts[i]
                        section_body = parts[i + 1]

                        regex_list = [r'Тема\s*\d+(?:\.\d+)*(?:[.:])?']
                        pattern = '(' + '|'.join(regex_list) + ')'

                        themes_parts = re.split(pattern, section_body)
                        section_name = themes_parts[0].strip()
                        if not section_name:
                            section_name = section_header.strip()

                        themes = []
                        if re.search(pattern, section_body):
                            for j in range(1, len(themes_parts), 2):
                                theme_title = themes_parts[j] + themes_parts[j + 1]
                                theme_title = self.__cut_by_words(theme_title, self.__endTextForTopics)
                                for r in regex_list:
                                    theme_title = re.sub(r'^' + r + r'\s*', '', theme_title)
                                theme_title = theme_title.strip(". ")
                                if not theme_title == "":
                                    themes.append(theme_title)
                            sections[section_name] = themes

                        else:
                            section_name = self.__cut_by_words(section_name, self.__endTextForTopics)
                            sections[section_name] = []

                    resultForAllTopics = sections
                    break

            return disciplineName, {
                "previousDisciplines": listOfPreviousDisciplines,
                "topics": resultForAllTopics
            }

        except Exception as e:
            print(f"{filePathDiscipline}: Error: {e}")
            return None, None
