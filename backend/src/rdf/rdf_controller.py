import pygraphdb
import requests
from requests.auth import HTTPBasicAuth


class RdfController:
    def __init__(self, host: str, port: str, user: str, password: str):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.url = f"http://{self.host}:{self.port}"

        self.db = None

    def open_connection(self, repository: str = None) -> bool:
        try:
            if repository:
                self.db = pygraphdb.connect(host=self.host, port=self.port, user=self.user,
                                            password=self.password, db=repository)
            else:
                self.db = pygraphdb.connect(host=self.host, port=self.port, user=self.user,
                                            password=self.password)
            return True
        except Exception as e:
            print("Error:", e)
            return False

    @staticmethod
    def update_str_data(data: str):
        specialSymbols = ['~', '.', '-', '!', '$', '&', "'", '(', ')', '*', '+', ',',
                          ';', '=', '/', '?', '#', '@', '%']
        data = data.replace(" ", "_")
        for symb in specialSymbols:
            data = data.replace(symb, "\\" + symb)
        return data

    def create_repo(self, repo_name: str) -> int:
        """Возвращает код ответа запроса"""
        """ВАЖНО!!! После создания нового репо перед выполнением с ним операций
        надо заново вызвать open_connection с передачей данного репо"""
        auth = HTTPBasicAuth(self.user, self.password)

        config = f'''
                @prefix rep: <http://www.openrdf.org/config/repository#> .
                @prefix sr: <http://www.openrdf.org/config/repository/sail#>.
                @prefix sail: <http://www.openrdf.org/config/sail#>.
            [] a rep:Repository ;
            rep:repositoryID "{repo_name}" ;
            rdfs:label "Main repo." ;
            rep:repositoryImpl [
                rep:repositoryType "graphdb:SailRepository" ;
                sr:sailImpl [
                    sail:sailType "graphdb:Sail" ;
                ]
            ].'''

        files = {'config': (f'{repo_name}.ttl', config, 'text/turtle')}

        response = requests.post(f"{self.url}/rest/repositories", files=files, auth=auth)

        return response.status_code

    def add_program(self, university: str, programData: dict) -> bool:
        if not self.db:
            return False

        cur = None

        if len(list(programData.keys())) == 0:
            return False

        programName = list(programData.keys())[0]

        programNameClean = self.update_str_data(programName)
        universityClean = self.update_str_data(university)

        try:
            cur = self.db.cursor()
            disciplines = []
            previousDisciplines = []
            topics = []
            subtopics = []
            for discipline in programData[programName]:
                for disciplineName, disciplineData in discipline.items():
                    disciplineNameClean = self.update_str_data(disciplineName)
                    disciplines.append(f"program:{universityClean}\/{programNameClean} program:hasDiscipline "
                                       f"discipline:{universityClean}\/{programNameClean}\/{disciplineNameClean} .")
                    for previousDiscipline in disciplineData["previousDisciplines"]:
                        previousDisciplineClean = self.update_str_data(previousDiscipline)
                        previousDisciplines.append(
                            f"discipline:{universityClean}\/{programNameClean}\/{previousDisciplineClean} "
                            f"discipline:previousDiscipline "
                            f"discipline:{universityClean}\/{programNameClean}\/{disciplineNameClean} .")
                    for topicsData in disciplineData["topics"]:
                        for topicName, subtopicsList in topicsData.items():
                            topicNameClean = self.update_str_data(topicName)
                            topics.append(
                                f"discipline:{universityClean}\/{programNameClean}\/{disciplineNameClean} "
                                f"discipline:hasTopic "
                                f"topic:{universityClean}\/{programNameClean}\/{disciplineNameClean}\/{topicNameClean} .")
                            for subtopic in subtopicsList:
                                subtopicClean = self.update_str_data(subtopic)
                                subtopics.append(
                                    f"topic:{universityClean}\/{programNameClean}\/{disciplineNameClean}\/{topicNameClean} "
                                    f"topic:hasSubtopic "
                                    f"subtopic:{universityClean}\/{programNameClean}\/{disciplineNameClean}\/{topicNameClean}\/{subtopicClean} .")

            cur.execute(
                f"""
                PREFIX univ: <http://universities/>
                PREFIX program: <http://programs/>
                PREFIX discipline: <http://disciplines/>
                PREFIX topic: <http://topics/>
                PREFIX subtopic: <http://subtopic>

                INSERT DATA {{
                    univ:{universityClean} univ:hasProgram program:{universityClean}\/{programNameClean} .
                    {"".join(disciplines)}
                    {"".join(previousDisciplines)}
                    {"".join(topics)}
                    {"".join(subtopics)}
                }}
                """
            )

            return True
        except Exception as e:
            print("Error:", e)
            return False
        finally:
            if cur:
                cur.close()

    def clear_repo(self):
        if not self.db:
            return False

        cur = None
        try:
            cur = self.db.cursor()
            cur.execute(
                f"""
                PREFIX univ: <http://universities/>
                PREFIX program: <http://programs/>
                PREFIX discipline: <http://disciplines/>
                PREFIX topic: <http://topics/>
                PREFIX subtopic: <http://subtopic>
                
                DELETE {{
                    ?s ?p ?o
                }} WHERE {{
                  ?s ?p ?o
                }};
                """
            )

            return True
        except Exception as e:
            print("Error:", e)
            return False
        finally:
            if cur:
                cur.close()

    def get_repo_all_data(self) -> list:
        result = self._select_all_data().split("\n")
        if len(result) <= 1:
            return []
        return result[1:]

    def _select_all_data(self) -> str | None:
        if not self.db:
            return None
        cur = None
        try:
            cur = self.db.cursor()
            result = cur.execute(
                f"""
                PREFIX univ: <http://universities/>
                PREFIX program: <http://programs/>
                PREFIX discipline: <http://disciplines/>
                PREFIX topic: <http://topics/>
                PREFIX subtopic: <http://subtopic>

                SELECT ?s ?p ?o
                WHERE {{
                    ?s ?p ?o .
                    FILTER (?p = univ:hasProgram || ?p = program:hasDiscipline || ?p = discipline:previousDiscipline || 
                            ?p = discipline:hasTopic || ?p = topic:hasSubtopic)
                }}
                """
            )

            return result
        except Exception as e:
            print("Error:", e)
            return None
        finally:
            if cur:
                cur.close()


    def close_connection(self):
        if self.db:
            self.db.close()
