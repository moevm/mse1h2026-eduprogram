from selenium.webdriver.support import expected_conditions as EC

from base.base_page import BasePage
from config.links import Links


class GraphPage(BasePage):
    PAGE_URL = Links.GRAPH

    def is_graph_displayed(self):
        self.wait.until(EC.visibility_of_element_located(("xpath", "//div[@class='graph-field-shell']"))).is_displayed()
