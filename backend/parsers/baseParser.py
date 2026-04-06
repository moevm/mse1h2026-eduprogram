from enum import Enum
from typing import List, Dict
from fastapi import UploadFile

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