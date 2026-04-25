from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select

from os import getcwd

from base.base_page import BasePage
from config.links import Links


class UploadProgramsPage(BasePage):
    PAGE_URL = Links.UPLOAD_PROGRAMS

    SELECT_UNIVERSITIES = ("xpath", "//select")
    FILE_INPUT = ("xpath", "//input[@type='file']")
    SEND_BUTTON = ("xpath", "//button[text()='Отправить']")

    def get_select_options(self):
        DROPDOWN_EL = Select(self.wait.until(EC.element_to_be_clickable(self.SELECT_UNIVERSITIES)))

        options_set = {option.text for option in DROPDOWN_EL.options}
        options_set.remove("Выберите университет")
        return options_set

    def select_by_name(self, university_name: str):
        DROPDOWN_EL = Select(self.wait.until(EC.element_to_be_clickable(self.SELECT_UNIVERSITIES)))
        DROPDOWN_EL.select_by_value(university_name)

    def input_file_by_path(self, file_path: str):
        FILE_INPUT_EL = self.wait.until(EC.presence_of_element_located(self.FILE_INPUT))

        FILE_INPUT_EL.send_keys(file_path)

    def click_send_button(self):
        self.wait.until(EC.element_to_be_clickable(self.SEND_BUTTON)).click()

    def get_alert_message(self):
        alert = self.wait.until(EC.alert_is_present())
        text = alert.text

        alert = self.driver.switch_to.alert
        alert.accept()
        return text
