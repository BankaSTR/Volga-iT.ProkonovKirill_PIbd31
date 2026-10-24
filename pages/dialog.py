import allure
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class Dialog:
    """Popup Maker dialog; all locators are scoped to one overlay."""

    def __init__(self, page, popup_id):
        self.page = page
        self.popup_id = popup_id
        self.root = (By.ID, f"pum-{popup_id}")

    def locator(self, selector):
        return By.CSS_SELECTOR, f"#pum-{self.popup_id} {selector}"

    @allure.step("Дождаться появления и завершения анимации окна")
    def wait_open(self):
        self.page.visible(self.root)
        self.page.wait.until(
            lambda _: (
                self.page.driver.find_element(*self.root).get_attribute("aria-modal") == "true"
            )
        )
        self.page.wait.until(
            lambda d: d.execute_script(
                "return !window.jQuery(arguments[0]).find('.pum-container').is(':animated')",
                self.page.driver.find_element(*self.root),
            )
        )
        return self

    @property
    def title(self):
        return self.page.visible(self.locator(".pum-title")).text

    @property
    def content(self):
        return self.page.visible(self.locator(".pum-content")).text

    @allure.step("Закрыть окно крестиком")
    def close(self):
        self.page.click(self.locator("button.pum-close"))
        self.page.hidden(self.root)

    @allure.step("Закрыть окно с клавиатуры кнопкой Enter")
    def close_with_keyboard(self):
        button = self.page.visible(self.locator("button.pum-close"))
        ActionChains(self.page.driver).move_to_element(button).perform()
        button.send_keys(Keys.ENTER)
        self.page.hidden(self.root)

    @allure.step("Нажать Escape")
    def escape(self):
        ActionChains(self.page.driver).send_keys(Keys.ESCAPE).perform()

    @allure.step("Нажать на подложку вне окна")
    def click_backdrop(self):
        # A point near the viewport corner, outside the centered container.
        ActionChains(self.page.driver).move_to_element_with_offset(
            self.page.driver.find_element(*self.root), 0, 0
        ).move_by_offset(
            -self.page.driver.get_window_size()["width"] // 2 + 15, 0
        ).click().perform()

    def assert_open(self):
        self.page.assert_stays_visible(self.root)

    def assert_closed(self):
        self.page.hidden(self.root)
        assert self.page.driver.find_element(*self.root).get_attribute("aria-modal") == "false"
