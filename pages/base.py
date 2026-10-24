from urllib.parse import urljoin

import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class BasePage:
    path = "/"

    def __init__(self, driver: WebDriver, base_url: str, timeout: float = 20):
        self.driver = driver
        self.base_url = base_url
        self.timeout = timeout
        self.wait = WebDriverWait(driver, timeout, poll_frequency=0.2)

    @allure.step("Открыть страницу упражнения")
    def open(self):
        self.driver.get(urljoin(self.base_url, self.path))
        self.visible((By.CSS_SELECTOR, "h1"))
        self.wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        return self

    def visible(self, locator: tuple[str, str]) -> WebElement:
        return self.wait.until(
            EC.visibility_of_element_located(locator), f"Element not visible: {locator}"
        )

    def click(self, locator):
        element = self.wait.until(
            EC.element_to_be_clickable(locator), f"Element not clickable: {locator}"
        )
        # Site-wide smooth scrolling can leave WebDriver's click point off-screen.
        # Scroll only; the actual click remains a native WebDriver action.
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center',behavior:'instant'})", element
        )
        self.wait.until(
            lambda d: d.execute_script(
                "const e=arguments[0],r=e.getBoundingClientRect();"
                "return e.contains(document.elementFromPoint(r.x+r.width/2,r.y+r.height/2))",
                element,
            )
        )
        element.click()

    def fill(self, locator, value):
        element = self.visible(locator)
        element.clear()
        if value:
            element.send_keys(value)

    def value(self, locator):
        return self.visible(locator).get_property("value")

    def hidden(self, locator):
        self.wait.until(
            EC.invisibility_of_element_located(locator), f"Element did not disappear: {locator}"
        )

    def assert_stays_visible(self, locator, seconds=1):
        """Observe the whole interval, so delayed closure cannot pass unnoticed."""
        from selenium.common.exceptions import TimeoutException

        try:
            WebDriverWait(self.driver, seconds, poll_frequency=0.1).until(
                EC.invisibility_of_element_located(locator)
            )
        except TimeoutException:
            return
        raise AssertionError(f"Element unexpectedly disappeared: {locator}")

    def assert_stays_hidden(self, locator, seconds=2):
        from selenium.common.exceptions import TimeoutException

        try:
            WebDriverWait(self.driver, seconds, poll_frequency=0.1).until(
                EC.visibility_of_element_located(locator)
            )
        except TimeoutException:
            return
        raise AssertionError(f"Element unexpectedly appeared: {locator}")
