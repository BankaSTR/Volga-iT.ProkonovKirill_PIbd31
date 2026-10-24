from datetime import date

import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

from pages.base import BasePage


class CalendarPage(BasePage):
    path = "/calendars/"
    INPUT = (By.CSS_SELECTOR, "#main input.jp-contact-form-date")
    PICKER = (By.CSS_SELECTOR, ".dp")
    MONTH = (By.CSS_SELECTOR, ".dp-cal-month")
    YEAR = (By.CSS_SELECTOR, ".dp-cal-year")
    SUCCESS = (By.CSS_SELECTOR, "#main .contact-form-submission.submission-success")
    FIELD_ERROR = (By.CSS_SELECTOR, "#main .contact-form__input-error.has-errors")

    @allure.step("Раскрыть календарь")
    def open_picker(self):
        def request_open(driver):
            if any(e.is_displayed() for e in driver.find_elements(*self.PICKER)):
                return True
            # Jetpack ignores open requests during its short closing transition.
            # Poll with native clicks until the widget is ready; never click an
            # already open picker, since another click would toggle it shut.
            self.click(self.INPUT)
            return False

        self.wait.until(request_open, "Date picker did not open after native input click")

    @property
    def displayed_month(self):
        return self.visible(self.MONTH).text, int(self.visible(self.YEAR).text)

    @allure.step("Выбрать {target} через переключатели года и месяца")
    def select_date(self, target: date):
        self.open_picker()
        self.click(self.YEAR)
        self.click((By.CSS_SELECTOR, f'.dp-year[data-year="{target.year}"]'))
        self.click(self.MONTH)
        self.click((By.CSS_SELECTOR, f'.dp-month[data-month="{target.month - 1}"]'))
        self.select_day(target.day)

    @allure.step("Перелистнуть месяц на {direction}")
    def move_month(self, direction):
        previous = self.displayed_month
        self.click((By.CSS_SELECTOR, ".dp-next" if direction > 0 else ".dp-prev"))
        self.wait.until(lambda _: self.displayed_month != previous)

    @allure.step("Выбрать день {day} текущего месяца")
    def select_day(self, day):
        self.click(
            (
                By.XPATH,
                f"//button[contains(concat(' ', @class, ' '), ' dp-day ') "
                f"and not(contains(@class, 'dp-edge-day')) and text()='{day}']",
            )
        )
        self.hidden(self.PICKER)

    @allure.step("Ввести дату вручную: {value}")
    def enter_date(self, value):
        self.fill(self.INPUT, value)
        self.visible(self.INPUT).send_keys(Keys.TAB)
        self.hidden(self.PICKER)

    @allure.step("Отправить дату")
    def submit(self):
        self.click((By.CSS_SELECTOR, "#main form button[type=submit]"))

    def wait_success(self):
        return self.visible(self.SUCCESS).text

    def wait_date_error(self):
        return self.visible(self.FIELD_ERROR).text

    @property
    def date_value(self):
        return self.value(self.INPUT)

    def assert_no_success(self):
        assert EC.invisibility_of_element_located(self.SUCCESS)(self.driver)
