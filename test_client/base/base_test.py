from pytest import fixture

from pages.login_page import LoginPage
from pages.register_page import RegisterPage
from pages.main_page import MainPage
from pages.upload_programs_page import UploadProgramsPage
from pages.graph import GraphPage
from pages.work_program_page import WorkProgramPage
from config.data import Data


class BaseTest:
    data: Data

    login_page: LoginPage
    register_page: RegisterPage
    main_page: MainPage
    upload_programs_page: UploadProgramsPage
    graph_page: GraphPage
    work_program_page: WorkProgramPage

    @fixture(autouse=True)
    def setup(self, driver, request):
        request.cls.driver = driver
        request.cls.data = Data()
        
        request.cls.login_page = LoginPage(driver)
        request.cls.register_page = RegisterPage(driver)
        request.cls.main_page = MainPage(driver)
        request.cls.upload_programs_page = UploadProgramsPage(driver)
        request.cls.graph_page = GraphPage(driver)
        request.cls.work_program_page = WorkProgramPage(driver)