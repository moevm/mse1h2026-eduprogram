from .rdf_controller import RdfController
import os
from dotenv import load_dotenv

load_dotenv()

_db_instance = None

repository = os.getenv('GRAPHDB_REPOSITORY')

def get_rdf():
    """Метод создания объекта контроллера RDF для дальнейшего открытия соединения и создания запросов"""
    global _db_instance
    if _db_instance is None:
        _db_instance = RdfController(os.getenv('GRAPHDB_HOST'), os.getenv('GRAPHDB_PORT'), os.getenv('GRAPHDB_USER'),
                                     os.getenv('GRAPHDB_PASSWORD'))
    return _db_instance
