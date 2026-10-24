import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from pages.base import BasePage
from pages.dialog import Dialog


class ModalsPage(BasePage):
    path = "/modals/"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.simple = Dialog(self, 1318)
        self.form = Dialog(self, 674)

    @allure.step("Открыть простое модальное окно")
    def open_simple(self):
        self.click((By.ID, "simpleModal"))
        return self.simple.wait_open()

    @allure.step("Открыть модальное окно с формой")
    def open_form(self):
        self.click((By.ID, "formModal"))
        return self.form.wait_open()

    def field(self, name):
        selectors = {"name": "input.name", "email": "input.email", "message": "textarea.textarea"}
        return self.form.locator(selectors[name])

    @allure.step("Заполнить контактную форму: имя={name}, email={email}")
    def fill_form(self, name="Volga IT", email="volga.it@example.com", message=""):
        for field, value in (("name", name), ("email", email), ("message", message)):
            self.fill(self.field(field), value)
        self.visible(self.field("message")).send_keys(Keys.TAB)

    @allure.step("Отправить контактную форму")
    def submit(self):
        self.click(self.form.locator("button[type=submit]"))

    def wait_success(self):
        return self.visible(self.form.locator(".contact-form-submission.submission-success")).text

    def field_error(self, name):
        self.wait.until(
            lambda _: self.visible(self.field(name)).get_attribute("aria-invalid") == "true"
        )
        return self.visible(
            self.form.locator(f".grunion-field-{name}-wrap .contact-form__input-error")
        ).text

    def assert_no_success(self):
        assert not any(
            e.is_displayed()
            for e in self.driver.find_elements(
                *self.form.locator(".contact-form-submission.submission-success")
            )
        )
