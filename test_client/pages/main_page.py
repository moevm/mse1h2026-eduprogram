from selenium.webdriver.support import expected_conditions as EC

from base.base_page import BasePage
from config.links import Links


class MainPage(BasePage):
    PAGE_URL = Links.MAIN

    CHOOSE_PROGRAM_BUTTON = ("xpath", "//button[child::span[text()='Выберите рабочую программу']]")
    ADD_PROGRAM_BUTTON = ("xpath", "//button[child::span[text()='Добавить программу']]")
    ADD_YOUR_PROGRAM_BUTTON = ("xpath", "//button[child::span[text()='Добавить свою программу']]")
    MODAL_WINDOW = ("xpath", "//div[@class='modal-overlay']")

    #локаторы модального окна с выбором графов
    # SHOW_PROGRAM_GRAPH_BUTTON = ("xpath", "//button[child::span[child::p[text()='Показать граф программы']]]")

    def click_choose_program_button(self):
        self.wait.until(EC.element_to_be_clickable(self.CHOOSE_PROGRAM_BUTTON)).click()

    def click_add_program_button(self):
        self.wait.until(EC.element_to_be_clickable(self.ADD_PROGRAM_BUTTON)).click()

    def is_modal_visible(self):
        self.wait.until(EC.visibility_of_element_located(self.MODAL_WINDOW))

    def click_add_your_program_button(self):
        self.wait.until(EC.element_to_be_clickable(self.ADD_YOUR_PROGRAM_BUTTON)).click()

    def click_show_program_graph_button_by_name(self, program_name: str):
        SHOW_PROGRAM_GRAPH_BUTTON = ("xpath", f"//li/span[text()='{program_name}']/following-sibling::button")

        self.wait.until(EC.element_to_be_clickable(SHOW_PROGRAM_GRAPH_BUTTON)).click()
