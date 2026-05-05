from base.base_test import BaseTest

from pytest import mark


@mark.order(3)
@mark.client
class TestAddYourProgram(BaseTest):
    def test_university_list(self, login_user, university_names):
        self.main_page.open()
        self.main_page.is_opened()

        self.main_page.click_add_your_program_button()
        self.upload_programs_page.is_opened()

        assert self.upload_programs_page.get_select_options() == university_names

        
    def test_upload_program_file(self, login_user):
        self.main_page.open()
        self.main_page.is_opened()

        self.main_page.click_add_your_program_button()
        self.upload_programs_page.is_opened()

        self.upload_programs_page.enter_program_name("test_program_name")

        self.upload_programs_page.select_by_name("СПБПУ")
        self.upload_programs_page.input_file_by_path(self.data.FILE)
        self.upload_programs_page.click_send_button()

        assert self.upload_programs_page.get_alert_message() == "Отправлено!"

        self.main_page.open()
        self.main_page.click_choose_program_button()
        self.main_page.click_show_program_graph_button_by_name("СПБПУ")

        self.graph_page.is_graph_displayed()
