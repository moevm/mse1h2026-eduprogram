import pygraphdb
import requests
from requests.auth import HTTPBasicAuth
import uuid
from io import BytesIO


class RdfController:
    def __init__(self, host: str, port: str, user: str, password: str):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.url = f"http://{self.host}:{self.port}"

        self.db = None
        self.repository = None

    def open_connection(self, repository: str = None) -> bool:
        try:
            if repository:
                self.db = pygraphdb.connect(host=self.host, port=self.port, user=self.user,
                                            password=self.password, db=repository)
                self.repository = repository
            else:
                self.db = pygraphdb.connect(host=self.host, port=self.port, user=self.user,
                                            password=self.password)
            return True
        except Exception as e:
            print("Error:", e)
            return False

    @staticmethod
    def convert_str_from_rdf_to_standard(data: str):
        data = data.replace("_", " ")
        return data.strip()

    @staticmethod
    def update_str_data(data: str):
        specialSymbols = ['~', '.', '-', '!', '$', '&', "'", '(', ')', '*', '+', ',',
                          ';', '=', '?', '#', '@', '%', '№', '>', '<']
        data = data.replace(" ", "_")
        data = data.replace("/", "_")
        data = data.replace(",", "_")
        for symb in specialSymbols:
            data = data.replace(symb, "\\" + symb)
        data = data.replace("«", "")
        data = data.replace("»", "")
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

    def _get_graphId_from_userId_university_program(self, idUser: int, university: str, programName: str) -> str:
        programNameClean = self.update_str_data(programName)
        universityUserIdClean = self.update_str_data(university + " id " + str(idUser))
        graphId = f"{universityUserIdClean}/{programNameClean}"
        return graphId

    def export_graph_as_file(self, graphId: str, fileFormat: str) -> BytesIO | None:
        """Возможные значения fileFormat: x-trig"""
        if not self.db or not self.repository:
            return None

        graphName = f"http://{graphId}"

        export_url = f"{self.url}/repositories/{self.repository}/rdf-graphs/service"
        params = {"graph": graphName}
        headers = {"Accept": f"application/{fileFormat}"}

        response = requests.get(export_url, headers=headers, params=params)

        file = BytesIO()
        file.write(response.content)

        file.seek(0)
        return file

    def clone_graph(self, idUser: int, university: str, programName: str) -> str | None:
        if not self.db:
            return None

        cur = None

        newGraphId = str(uuid.uuid4())

        try:
            cur = self.db.cursor()
            cur.execute(
                f"""
                PREFIX univ: <http://universities/>
                PREFIX program: <http://programs/>
                PREFIX discipline: <http://disciplines/>
                PREFIX topic: <http://topics/>
                PREFIX subtopic: <http://subtopic/>

                INSERT {{
                    GRAPH <http://{newGraphId}> {{
                        ?s ?p ?o
                    }}
                }}
                
                WHERE {{
                    GRAPH <http://{self._get_graphId_from_userId_university_program(idUser, university, programName)}> {{
                        ?s ?p ?o
                    }}
                }}
                """
            )
            return newGraphId
        except Exception as e:
            print("Error:", e)
            return None
        finally:
            if cur:
                cur.close()


    def add_percentage_of_subtopic_overlap(self, graphId: str, idUser: int, university: str, programName: str,
                                           disciplineName: str,
                                           topicName: str, subtopicName: str, overlapValue: int) -> bool:
        if not self.db:
            return False

        cur = None

        programNameClean = self.update_str_data(programName)
        universityUserIdClean = self.update_str_data(university + " id " + str(idUser))
        disciplineNameClean = self.update_str_data(disciplineName)
        topicNameClean = self.update_str_data(topicName)
        subtopicNameClean = self.update_str_data(subtopicName)

        try:
            cur = self.db.cursor()
            cur.execute(
                f"""
                PREFIX univ: <http://universities/>
                PREFIX program: <http://programs/>
                PREFIX discipline: <http://disciplines/>
                PREFIX topic: <http://topics/>
                PREFIX subtopic: <http://subtopic/>

                INSERT DATA {{
                    GRAPH <http://{graphId}> {{
                        subtopic:{universityUserIdClean}\/{programNameClean}\/{disciplineNameClean}\/{topicNameClean}\/{subtopicNameClean}
                        subtopic:hasOverlap
                        {overlapValue} .
                    }}
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


    def add_program(self, university: str, programData: dict, idUser: int) -> bool:
        if not self.db:
            return False

        cur = None

        if len(list(programData.keys())) == 0:
            return False

        programName = list(programData.keys())[0]

        programNameClean = self.update_str_data(programName)
        universityUserIdClean = self.update_str_data(university + " id " + str(idUser))

        try:
            cur = self.db.cursor()
            disciplines = []
            previousDisciplines = []
            topics = []
            subtopics = []
            for discipline in programData[programName]:
                for disciplineName, disciplineData in discipline.items():
                    disciplineNameClean = self.update_str_data(disciplineName)
                    disciplines.append(f"program:{universityUserIdClean}\/{programNameClean} program:hasDiscipline "
                                       f"discipline:{universityUserIdClean}\/{programNameClean}\/{disciplineNameClean} .")
                    for previousDiscipline in disciplineData["previousDisciplines"]:
                        previousDisciplineClean = self.update_str_data(previousDiscipline)
                        previousDisciplines.append(
                            f"discipline:{universityUserIdClean}\/{programNameClean}\/{previousDisciplineClean} "
                            f"discipline:previousDiscipline "
                            f"discipline:{universityUserIdClean}\/{programNameClean}\/{disciplineNameClean} .")

                        try:
                            cur.execute(
                                f"""
                                PREFIX univ: <http://universities/>
                                PREFIX program: <http://programs/>
                                PREFIX discipline: <http://disciplines/>
                                PREFIX topic: <http://topics/>
                                PREFIX subtopic: <http://subtopic/>

                                INSERT DATA {{
                                    GRAPH <http://{self._get_graphId_from_userId_university_program(idUser, university, programName)}> {{
                                        {previousDisciplines[-1] if len(previousDisciplines) > 0 else ""}
                                    }}
                                }}
                                """
                            )
                        except Exception as e:
                            print(f"Incorrect previousDiscipline: {previousDiscipline}. ", e)
                            continue
                    for topicsData in disciplineData["topics"]:
                        for topicName, subtopicsList in topicsData.items():
                            topicNameClean = self.update_str_data(topicName)
                            topics.append(
                                f"discipline:{universityUserIdClean}\/{programNameClean}\/{disciplineNameClean} "
                                f"discipline:hasTopic "
                                f"topic:{universityUserIdClean}\/{programNameClean}\/{disciplineNameClean}\/{topicNameClean} .")
                            for subtopic in subtopicsList:
                                subtopicClean = self.update_str_data(subtopic)
                                subtopics.append(
                                    f"topic:{universityUserIdClean}\/{programNameClean}\/{disciplineNameClean}\/{topicNameClean} "
                                    f"topic:hasSubtopic "
                                    f"subtopic:{universityUserIdClean}\/{programNameClean}\/{disciplineNameClean}\/{topicNameClean}\/{subtopicClean} .")

                                try:
                                    cur.execute(
                                        f"""
                                        PREFIX univ: <http://universities/>
                                        PREFIX program: <http://programs/>
                                        PREFIX discipline: <http://disciplines/>
                                        PREFIX topic: <http://topics/>
                                        PREFIX subtopic: <http://subtopic/>

                                        INSERT DATA {{
                                            GRAPH <http://{self._get_graphId_from_userId_university_program(idUser, university, programName)}> {{
                                                {subtopics[-1] if len(subtopics) > 0 else ""}
                                            }}
                                        }}
                                        """
                                    )
                                except Exception as e:
                                    print(f"Incorrect subtopic: {subtopic}. ", e)
                                    continue

                            try:
                                cur.execute(
                                    f"""
                                    PREFIX univ: <http://universities/>
                                    PREFIX program: <http://programs/>
                                    PREFIX discipline: <http://disciplines/>
                                    PREFIX topic: <http://topics/>
                                    PREFIX subtopic: <http://subtopic/>

                                    INSERT DATA {{
                                        GRAPH <http://{self._get_graphId_from_userId_university_program(idUser, university, programName)}> {{
                                            {topics[-1] if len(topics) > 0 else ""}
                                        }}
                                    }}
                                    """
                                )
                            except Exception as e:
                                print(f"Incorrect topic: {topicName}. ", e)
                                continue

                    try:
                        cur.execute(
                            f"""
                            PREFIX univ: <http://universities/>
                            PREFIX program: <http://programs/>
                            PREFIX discipline: <http://disciplines/>
                            PREFIX topic: <http://topics/>
                            PREFIX subtopic: <http://subtopic/>
    
                            INSERT DATA {{
                                GRAPH <http://{universityUserIdClean}/{programNameClean}> {{
                                    {disciplines[-1] if len(disciplines) > 0 else ""}
                                }}
                            }}
                            """
                        )
                    except Exception as e:
                        print(f"Incorrect discipline: {disciplineName}. ", e)
                        continue


            cur.execute(
                f"""
                PREFIX univ: <http://universities/>
                PREFIX program: <http://programs/>
                PREFIX discipline: <http://disciplines/>
                PREFIX topic: <http://topics/>
                PREFIX subtopic: <http://subtopic/>

                INSERT DATA {{
                    GRAPH <http://{self._get_graphId_from_userId_university_program(idUser, university, programName)}> {{
                        univ:{universityUserIdClean} univ:hasProgram program:{universityUserIdClean}\/{programNameClean} 
                    }}.
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
                PREFIX subtopic: <http://subtopic/>
                
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

    def get_data_of_user(self, idUser: int) -> list:
        rows = self._select_data_of_idUser(idUser).split("\n")
        if len(rows) <= 1:
            return []
        result = set()
        for row in rows:
            try:
                subject = row.split(',')[0]
                if 'http://programs/' in subject:
                    program = subject.split('/')[-1]
                    university = subject.split('/')[-2]
                    program = program.replace("_", " ")
                    university = university.split("_id_")[0].replace("_", " ")
                    result.add((university, program))
            except Exception as e:
                continue
        return list(result)

    def get_data_of_university_and_program(self, universityName: str, programName: str, idUser: int) -> dict:
        universityUserIdNameClean = self.update_str_data(universityName + " id " + str(idUser))
        programNameClean = self.update_str_data(programName)
        graphName = f"<http://{universityUserIdNameClean}/{programNameClean}>"
        result = self._select_data_from_graph(graphName).split("\n")
        return self._convert_rdf_rows_to_json(programName, result)

    def get_data_of_graph(self, graphId: str, programName: str) -> dict:
        graphName = f"<http://{graphId}>"
        result = self._select_data_from_graph(graphName).split("\n")
        return self._convert_rdf_rows_to_json(programName, result)

    def _select_all_graphs(self) -> str | None:
        query = f"""
                PREFIX univ: <http://universities/>
                PREFIX program: <http://programs/>
                PREFIX discipline: <http://disciplines/>
                PREFIX topic: <http://topics/>
                PREFIX subtopic: <http://subtopic/>

                SELECT DISTINCT ?g WHERE {{
                    GRAPH ?g {{
                        ?s ?p ?o
                    }}
                }}

                """
        return self._select_operation(query)

    def _convert_rdf_rows_to_json(self, programName: str, rows: list) -> dict:
        if len(rows) <= 1:
            return {}
        jsonProgram = {}
        for row in rows:
            try:
                predicat = row.split(',')[1]
                if 'programs/hasDiscipline' in predicat:
                    subject = row.split(',')[0]
                    object = row.split(',')[2]
                    discipline = self.convert_str_from_rdf_to_standard(object.split('/')[-1])
                    jsonProgram[discipline] = {"previousDisciplines": [], "topics": {}}
            except Exception as e:
                continue
        for row in rows:
            try:
                predicat = row.split(',')[1]
                if 'disciplines/previousDiscipline' in predicat:
                    subject = row.split(',')[0]
                    object = row.split(',')[2]
                    disciplineCurrent = self.convert_str_from_rdf_to_standard(subject.split('/')[-1])
                    disciplinePrevious = self.convert_str_from_rdf_to_standard(object.split('/')[-1])
                    jsonProgram[disciplinePrevious]["previousDisciplines"].append(disciplineCurrent)
            except Exception as e:
                continue

        for row in rows:
            try:
                predicat = row.split(',')[1]
                if 'disciplines/hasTopic' in predicat:
                    subject = row.split(',')[0]
                    object = row.split(',')[2]
                    discipline = self.convert_str_from_rdf_to_standard(subject.split('/')[-1])
                    topic = self.convert_str_from_rdf_to_standard(object.split('/')[-1])
                    jsonProgram[discipline]["topics"][topic] = {"subtopics": {}}
            except Exception as e:
                continue

        for row in rows:
            try:
                predicat = row.split(',')[1]
                if 'topics/hasSubtopic' in predicat:
                    subject = row.split(',')[0]
                    object = row.split(',')[2]
                    topic = self.convert_str_from_rdf_to_standard(subject.split('/')[-1])
                    discipline = self.convert_str_from_rdf_to_standard(subject.split('/')[-2])
                    subtopic = self.convert_str_from_rdf_to_standard(object.split('/')[-1])
                    jsonProgram[discipline]["topics"][topic]["subtopics"][subtopic] = {}
            except Exception as e:
                continue

        for row in rows:
            try:
                predicat = row.split(',')[1]
                if 'subtopic/hasOverlap' in predicat:
                    subject = row.split(',')[0]
                    object = row.split(',')[2]
                    subtopic = self.convert_str_from_rdf_to_standard(subject.split('/')[-1])
                    topic = self.convert_str_from_rdf_to_standard(subject.split('/')[-2])
                    discipline = self.convert_str_from_rdf_to_standard(subject.split('/')[-3])
                    overlap = int(object)
                    jsonProgram[discipline]["topics"][topic]["subtopics"][subtopic]["overlapValue"] = overlap
            except Exception as e:
                continue

        return {programName: jsonProgram}

    def _select_all_data(self) -> str | None:
        query = f"""
                PREFIX univ: <http://universities/>
                PREFIX program: <http://programs/>
                PREFIX discipline: <http://disciplines/>
                PREFIX topic: <http://topics/>
                PREFIX subtopic: <http://subtopic/>

                SELECT ?s ?p ?o
                WHERE {{
                    ?s ?p ?o .
                    FILTER (?p = univ:hasProgram || ?p = program:hasDiscipline || ?p = discipline:previousDiscipline || 
                            ?p = discipline:hasTopic || ?p = topic:hasSubtopic)
                }}
                """
        return self._select_operation(query)

    def _select_data_from_graph(self, graphName: str) -> str | None:
        query = f"""
                PREFIX univ: <http://universities/>
                PREFIX program: <http://programs/>
                PREFIX discipline: <http://disciplines/>
                PREFIX topic: <http://topics/>
                PREFIX subtopic: <http://subtopic/>
                
                SELECT ?s ?p ?o FROM NAMED {graphName} {{
                  GRAPH ?g {{
                    ?s ?p ?o
                  }}
                }}
                """
        return self._select_operation(query)

    def _select_data_of_idUser(self, idUser: int) -> str | None:
        query = f"""
                PREFIX univ: <http://universities/>
                PREFIX program: <http://programs/>
                PREFIX discipline: <http://disciplines/>
                PREFIX topic: <http://topics/>
                PREFIX subtopic: <http://subtopic/>

                SELECT ?s ?p ?o
                WHERE {{
                    ?s ?p ?o .
                    FILTER(CONTAINS(STR(?o), "_id_{str(idUser)}") || 
                    CONTAINS(STR(?s), "_id_{str(idUser)}"))
                }}
                """
        return self._select_operation(query)

    def _select_operation(self, query: str):
        if not self.db:
            return None
        cur = None
        try:
            cur = self.db.cursor()
            result = cur.execute(
                query
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
