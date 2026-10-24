import allure
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

pytestmark = [pytest.mark.ads, allure.feature("Рекламное окно")]


@pytest.mark.positive
@pytest.mark.smoke
@allure.title("ADS-P01: Реклама автоматически появляется с задержкой")
def test_delayed_appearance(ads):
    # Navigation Timing includes the time spent in driver.get and page setup.
    elapsed = ads.driver.execute_script("return performance.now()")
    # On slow networks navigation may finish after the ad timer. Assert the
    # pre-popup state only when it is still observable, without skipping the test.
    if elapsed < 4000:
        assert not ads.driver.find_element(*ads.ad.root).is_displayed(), "Ad appeared too early"
    ads.ad.wait_open()
    assert ads.driver.execute_script("return performance.now()") >= 4000


@pytest.mark.positive
@allure.title("ADS-P02: Рекламное окно содержит ожидаемый текст и кнопку закрытия")
def test_ad_content(ads):
    dialog = ads.ad.wait_open()
    assert dialog.title == "Hi"
    assert dialog.content == "I am an ad."
    assert ads.visible(dialog.locator("button.pum-close")).get_attribute("aria-label") == "Close"


@pytest.mark.positive
@allure.title("ADS-P03: Крестик закрывает рекламу и разблокирует страницу")
def test_close_restores_page(ads):
    dialog = ads.ad.wait_open()
    dialog.close()
    dialog.assert_closed()
    assert "pum-open" not in ads.driver.find_element(By.TAG_NAME, "html").get_attribute("class")
    ads.click((By.CSS_SELECTOR, ".breadcrumbs a"))
    ads.wait.until(lambda d: d.current_url.rstrip("/") == ads.base_url.rstrip("/"))


@pytest.mark.positive
@allure.title("ADS-P04: Рекламу можно закрыть клавишей Enter на крестике")
def test_keyboard_close(ads):
    dialog = ads.ad.wait_open()
    dialog.close_with_keyboard()
    dialog.assert_closed()


@pytest.mark.positive
@allure.title("ADS-P05: После обновления закрытая реклама появляется заново")
def test_refresh_reopens(ads):
    ads.ad.wait_open().close()
    ads.driver.refresh()
    ads.ad.wait_open()
    assert ads.ad.content == "I am an ad."


@pytest.mark.positive
@allure.title("ADS-P06: Повторный переход на страницу снова показывает рекламу")
def test_return_reopens(ads):
    ads.ad.wait_open().close()
    ads.driver.get(ads.base_url)
    ads.open()
    ads.ad.wait_open()
    assert ads.ad.title == "Hi"


@pytest.mark.positive
@allure.title("ADS-P07: Окно и крестик доступны в узком окне браузера")
def test_narrow_viewport(ads):
    ads.driver.set_window_size(600, 800)
    dialog = ads.ad.wait_open()
    button = ads.visible(dialog.locator("button.pum-close"))
    width = ads.driver.execute_script("return window.innerWidth")
    assert 0 <= button.rect["x"] < button.rect["x"] + button.rect["width"] <= width
    dialog.close()
    dialog.assert_closed()


@pytest.mark.negative
@allure.title("ADS-N01: Escape не закрывает рекламу")
def test_escape_ignored(ads):
    dialog = ads.ad.wait_open()
    dialog.escape()
    dialog.assert_open()


@pytest.mark.negative
@allure.title("ADS-N02: Нажатие на подложку не закрывает рекламу")
def test_backdrop_ignored(ads):
    dialog = ads.ad.wait_open()
    dialog.click_backdrop()
    dialog.assert_open()


@pytest.mark.negative
@allure.title("ADS-N03: Закрытая реклама не появляется повторно без перезагрузки")
def test_no_repeated_ad(ads):
    ads.ad.wait_open().close()
    # Observe longer than the initial 4.5 s timer; fail on any reappearance.
    from selenium.common.exceptions import TimeoutException

    try:
        WebDriverWait(ads.driver, 5.5, poll_frequency=0.1).until(
            lambda d: d.find_element(*ads.ad.root).is_displayed()
        )
    except TimeoutException:
        return
    pytest.fail("Ad appeared again without page navigation")
