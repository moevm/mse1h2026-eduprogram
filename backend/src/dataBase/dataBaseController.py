import psycopg2.pool
import hashlib

class DataBaseController:
    """Контроллер базы данных по хранению пользователей и файлов университетов"""
    def __init__(self, dbName: str, host: str, port: str, user: str, password: str,
                 minConnNumber: int, maxConnNumber: int):
        self.__dbName = dbName
        self.__host = host
        self.__port = port
        self.__user = user
        self.__password = password
        self.__minConnNumber = minConnNumber
        self.__maxConnNumber = maxConnNumber
        self.__poolConnections = None

        self.__tableUsers = "users"
        self.__tableUsersFields = ["login", "password_hash"]

        self.__tableUserFolder = "user_folders"
        self.__tableUserFolderFields = ["idUser", "folder_name"]

        self.__tableWorkPrograms = "uploaded_files"
        self.__tableWorkProgramsFields = ["idUser", "folder_name", "file_path"]

    def openConnection(self) -> bool:
        """Метод создания пулла соединений"""
        if not self.__dbName:
            return False
        try:
            self.__poolConnections = (
                psycopg2.pool.SimpleConnectionPool(self.__minConnNumber, self.__maxConnNumber,
                                                   database=self.__dbName, host=self.__host, port=self.__port,
                                                   user=self.__user, password=self.__password))
            return True
        except Exception as e:
            print("Error:", e)
            return False

    def closeConnection(self):
        """Метод закрытия пулла соединения"""
        if not self.isConnected():
            return
        self.__poolConnections.closeall()

    def isConnected(self) -> bool:
        """Метод проверки соединения с БД"""
        return self.__poolConnections is not None

    @staticmethod
    def __getHashByLoginPwd(login: str, password: str) -> str:
        """Получение хэша для логина и пароля пользователя"""
        combinedStr = f"{login}:{password}"
        hashByLoginPwd = hashlib.sha256(combinedStr.encode('utf-8'))
        return hashByLoginPwd.hexdigest()

    def __insertOperation(self, request: str, args: tuple) -> bool:
        if not self.isConnected():
            return False

        connection = None
        cursor = None
        try:
            connection = self.__poolConnections.getconn()
            if not connection:
                return False
            cursor = connection.cursor()
            if not cursor:
                return False
            cursor.execute(request, args)
            connection.commit()
            return True
        except Exception as e:
            print("Error:", e)
            if connection:
                connection.rollback()
            return False
        finally:
            cursor.close()
            self.__poolConnections.putconn(connection)

    def __findOperation(self, request: str, args: tuple) -> list:
        if not self.isConnected():
            return []

        connection = None
        cursor = None
        try:
            connection = self.__poolConnections.getconn()
            if not connection:
                return []
            cursor = connection.cursor()
            if not cursor:
                return []
            cursor.execute(request, args)
            return cursor.fetchall()
        except Exception as e:
            print("Error:", e)
            if connection:
                connection.rollback()
            return []
        finally:
            cursor.close()
            self.__poolConnections.putconn(connection)

    def addWorkProgram(self, idUser: int, folderName: str, filePath: str) -> bool:
        """Метода добавления рабочей программы в базу данных.
        Возвращает true, если пользователь был успешно добавлен"""
        request = f"INSERT INTO {self.__tableWorkPrograms} ({", ".join(self.__tableWorkProgramsFields)}) VALUES (%s, %s, %s);"
        args = (idUser, folderName, filePath)
        return self.__insertOperation(request, args)

    def addUserFolder(self, idUser: int, filePath: str) -> bool:
        """Метода добавления папки пользователя в базу данных.
        Возвращает true, если пользователь был успешно добавлен"""
        request = f"INSERT INTO {self.__tableUserFolder} ({", ".join(self.__tableUserFolderFields)}) VALUES (%s, %s);"
        args = (idUser, filePath)
        return self.__insertOperation(request, args)

    def addUser(self, login: str, password: str) -> bool:
        """Метода добавления пользователя в базу данных.
        Возвращает true, если пользователь был успешно добавлен"""

        userHash = self.__getHashByLoginPwd(login, password)
        request = f"INSERT INTO {self.__tableUsers} ({", ".join(self.__tableUsersFields)}) VALUES (%s, %s);"
        args = (login, userHash)
        return self.__insertOperation(request, args)

    def findUserByLoginPassword(self, login: str, password: str) -> dict:
        """Метод нахождения пользователя по логину/паролю из БД.
        Возвращает словарь {id: integer}"""

        userHash = self.__getHashByLoginPwd(login, password)
        request = f"SELECT * from {self.__tableUsers} WHERE password_hash = %s"
        args = (userHash,)
        resultSelect = self.__findOperation(request, args)
        if not resultSelect:
            return {}
        user = resultSelect[0]
        if user:
            return {"id": user[0]}
        return {}

    def findUserById(self, idUser: int) -> dict:
        """Метод нахождения пользователя по id из БД.
        Возвращает словарь {id: integer, login: str}"""

        request = f"SELECT * from {self.__tableUsers} WHERE id = %s"
        args = (idUser,)
        resultSelect = self.__findOperation(request, args)
        if not resultSelect:
            return {}
        user = resultSelect[0]
        if len(user) >= 2:
            return {"id": user[0], "login": user[1]}
        return {}
