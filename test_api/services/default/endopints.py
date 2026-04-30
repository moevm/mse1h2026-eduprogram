from test_api.config.data import Data


class Endpoints:
    host = Data.host
    login = f"{host}/login"
    registration = f"{host}/registration"
    add_program = f"{host}/add-program"
    get_programs = f"{host}/get-programs"
    show_graph = f"{host}/show-graph"
    get_available_universities = f"{host}/get-available-universities"
    add_program_from_files = f"{host}/add-program-from-files"