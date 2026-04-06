from src.dataBase.dependencies import get_db

def appendParsers():
    db = get_db()
    db.openConnection()
    # Хардкод неприятный, может есть смысл добавить метод в интерфейс парсера getUniversityName -> str.
    # Тогда всю будет соответствовать указанной мапе.
    db.addParser("ГУАП", 0)
    db.addParser("СПБГЭТУ ЛЭТИ", 1)
    db.addParser("МПУ", 2)
    db.addParser("МТУСИ", 3)
    db.addParser("СПБПУ", 4)


### Моё предложение 

class ParserType(str, Enum):
    GUAP = "ГУАП"
    LETI = "СПБГЭТУ ЛЭТИ"
    MPY = "МПУ"
    MTYSI = "МТУСИ"
    POLITEH = "СПБПУ"

class BaseParser:
    def get_type(self) -> ParserType:
        raise NotImplementedError
    
    async def parse(self, nameDirection: str, files: List[UploadFile]) -> Dict:
        """Асинхронный парсинг файлов"""
        raise NotImplementedError

class SomeParser(BaseParser):
    def get_type(self) -> ParserType:
        return ParserType.LETI
    async def parse(self, nameDirection: str, files: List[UploadFile]) -> Dict:
        ...

class ParsersContainer:
    def __init__(self):
        self._parsers: Dict[ParserType, BaseParser] = {}
        self._register_parsers()
    
    def _register_parsers(self):
        """Регистрация всех парсеров при инициализации"""
        parsers = [
            ParserGUAP(),
            ParserLETI(),
            ParserMPU(),
            ParserMTUCI(),
            ParserSpbPU()
        ]
        for parser in parsers:
            self._parsers[parser.get_type()] = parser
    
    def register_parser(self, parser: BaseParser) -> None:
        """Регистрация парсера"""
        parser_type = parser.get_type()
        self._parsers[parser_type] = parser
    
    def get_parser(self, parser_type: ParserType) -> Optional[BaseParser]:
        """Получение парсера по типу"""
        return self._parsers.get(parser_type)
    
    def has_parser(self, parser_type: ParserType) -> bool:
        """Проверка наличия парсера"""
        return parser_type in self._parsers
    
    def parse_by_type(self, parser_type: ParserType, files: List[UploadFile]) -> Dict:
        """Парсинг файлов указанным парсером"""
        parser = self.get_parser(parser_type)
        if not parser:
            raise ValueError(f"No parser found for type: {parser_type}")
        return parser.parse(files)
    
    def get_all_parsers(self) -> List[ParserType]:
        """Получение списка всех зарегистрированных парсеров"""
        return list(self._parsers.keys())

###


if __name__ == "__main__":
    appendParsers()