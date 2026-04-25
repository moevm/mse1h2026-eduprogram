from base.base_test import BaseTest

from pytest import mark


@mark.order(4)
class TestAddProgram(BaseTest):
    def test_add_program(self, login_user):
        self.main_page.open()
        self.main_page.is_opened()

        self.main_page.click_add_program_button()
        self.work_program_page.is_opened()

        self.work_program_page.input_program_with_name("TEST_PROGRAM")
        self.work_program_page.input_node_by_index(1, "Метил")

        self.work_program_page.click_add_discipline_button()
        self.work_program_page.input_node_by_index(2, "Этил")

        self.work_program_page.click_add_discipline_button()
        self.work_program_page.input_node_by_index(3, "Мутил")

        self.work_program_page.input_previous_by_index(3, "Метил")
        self.work_program_page.click_add_previous_by_index(3)

        self.work_program_page.input_previous_by_index(3, "Этил")
        self.work_program_page.click_add_previous_by_index(3)

        self.work_program_page.click_submit_button()

        self.work_program_page.accept_alert()

        self.main_page.open()
        self.main_page.click_choose_program_button()
        self.main_page.click_show_program_graph_button_by_name("TEST_PROGRAM")

        self.graph_page.is_graph_displayed()



