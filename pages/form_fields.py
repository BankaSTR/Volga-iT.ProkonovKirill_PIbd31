import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.base import BasePage


class FormFieldsPage(BasePage):
    path = "/form-fields/"
    TOOLS = (By.XPATH, "//label[normalize-space()='Automation tools']/following-sibling::ul[1]/li")
    MESSAGE = (By.ID, "message")

    @allure.step("Прочитать элементы Automation Tools через Selenium")
    def automation_tools(self):
        elements = self.wait.until(EC.visibility_of_all_elements_located(self.TOOLS))
        return [element.text.strip() for element in elements]

    @allure.step("Заполнить Message названиями инструментов через запятую")
    def fill_tools_message(self, tools):
        text = ", ".join(tools)
        self.fill(self.MESSAGE, text)
        return text

    @allure.step("Отправить форму и прочитать JavaScript alert")
    def submit(self, name="Volga IT"):
        self.fill((By.ID, "name-input"), name)
        self.click((By.ID, "submit-btn"))
        alert = self.wait.until(EC.alert_is_present())
        text = alert.text
        alert.accept()
        return text
