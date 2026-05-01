from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select

from os import getcwd

from base.base_page import BasePage
from config.links import Links


class WorkProgramPage(BasePage):
    PAGE_URL = Links.WORK_PROGRAM

    PROGRAM_INPUT = ("xpath", "//input[@class='program-input']")
    ADD_DISCIPLINE_BUTTON = ("xpath", "//button[text()='Добавить дисциплину']")
    SUBMIT_BUTTON = ("xpath", "//button[@class='submit-btn']")

    def input_program_with_name(self, program_name: str):
        self.wait.until(EC.visibility_of_element_located(self.PROGRAM_INPUT)).send_keys(program_name)

    def click_add_discipline_button(self):
        self.wait.until(EC.element_to_be_clickable(self.ADD_DISCIPLINE_BUTTON)).click()

    def input_node_by_index(self, index: int, value: str):
        self.wait.until(EC.visibility_of_element_located(("xpath", f"//div[@class='tree-node'][{index}]//input[@class='node-input']"))).send_keys(value)

    def input_previous_by_index(self, index: int, value: str):
        self.wait.until(EC.visibility_of_element_located(("xpath", "//div[@class='tree-node'][3]/div[@class='prev-disciplines']//input"))).send_keys(value)

    def click_add_previous_by_index(self, index: int):
        self.wait.until(EC.element_to_be_clickable(("xpath", "//div[@class='tree-node'][3]/div[@class='prev-disciplines']//button[text()='+']"))).click()

    def click_submit_button(self):
        self.wait.until(EC.element_to_be_clickable(self.SUBMIT_BUTTON)).click()

    def accept_alert(self):
        self.wait.until(EC.alert_is_present()).accept()