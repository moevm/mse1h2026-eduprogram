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
        self.__tableUsersFields = ["hash_login_password"]

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

    def addUser(self, login: str, password: str) -> bool:
        """Метода добавления пользователя в базу данных.
        Возвращает true, если пользователь был успешно добавлен"""
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
            userHash = self.__getHashByLoginPwd(login, password)
            cursor.execute(f"INSERT INTO {self.__tableUsers} ({", ".join(self.__tableUsersFields)}) VALUES (%s);",
                           (userHash,))
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

    def findUser(self, login: str, password: str) -> dict:
        """Метод нахождения пользователя из БД.
        Возвращает словарь {id: integer}"""
        """TODO: Есть небольшое дублирование. В дальнейшем можно подумать, как исправить"""
        if not self.isConnected():
            return {}

        connection = None
        cursor = None
        try:
            connection = self.__poolConnections.getconn()
            if not connection:
                return {}
            cursor = connection.cursor()
            if not cursor:
                return {}
            userHash = self.__getHashByLoginPwd(login, password)
            cursor.execute(f"SELECT * from {self.__tableUsers} WHERE hash_login_password = %s", (userHash,))
            resultSelect = cursor.fetchone()
            if resultSelect:
                return {"id": resultSelect[0]}
            return {}
        except Exception as e:
            print("Error:", e)
            if connection:
                connection.rollback()
            return {}
        finally:
            cursor.close()
            self.__poolConnections.putconn(connection)
