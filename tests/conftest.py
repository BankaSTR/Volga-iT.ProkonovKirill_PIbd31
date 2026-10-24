import json
import logging
import os
import platform
from pathlib import Path

import allure
import pytest
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService

from pages.ads import AdsPage
from pages.calendar import CalendarPage
from pages.form_fields import FormFieldsPage
from pages.modals import ModalsPage

LOGGER = logging.getLogger(__name__)


def positive_float(value):
    number = float(value)
    if not 0 < number <= 300:
        raise pytest.UsageError("Timeout must be in the range (0, 300] seconds")
    return number


def pytest_addoption(parser):
    group = parser.getgroup("ui", "Selenium browser options")
    group.addoption("--browser", choices=["chrome", "firefox"], default="chrome")
    group.addoption("--headed", action="store_true", help="Show the browser window")
    group.addoption("--base-url", default=os.getenv("BASE_URL", "https://practice-automation.com/"))
    group.addoption("--timeout", type=positive_float, default=20, help="Explicit wait, seconds")
    group.addoption("--page-load-timeout", type=positive_float, default=60)
    group.addoption("--browser-binary", default=None, help="Optional browser executable")
    group.addoption("--driver-path", default=None, help="Optional offline WebDriver executable")


def pytest_configure(config):
    if hasattr(config, "workerinput"):
        return
    results = Path(config.getoption("allure_report_dir") or "allure-results")
    results.mkdir(parents=True, exist_ok=True)
    (results / "environment.properties").write_text(
        f"Python={platform.python_version()}\nSelenium={selenium.__version__}\n"
        f"Browser={config.getoption('--browser')}\nOS={platform.platform()}\n"
        f"Base.URL={config.getoption('--base-url')}\n"
        f"Headless={not config.getoption('--headed')}\n",
        encoding="utf-8",
    )


def attach_diagnostics(driver, phase):
    """A diagnostics failure must never replace the original test failure."""
    for name, kind, capture in (
        ("Screenshot", allure.attachment_type.PNG, driver.get_screenshot_as_png),
        ("Page DOM", allure.attachment_type.HTML, lambda: driver.page_source),
        ("URL", allure.attachment_type.TEXT, lambda: driver.current_url),
        (
            "Browser capabilities",
            allure.attachment_type.JSON,
            lambda: json.dumps(driver.capabilities, indent=2),
        ),
    ):
        try:
            allure.attach(capture(), name=f"{phase}: {name}", attachment_type=kind)
        except Exception:
            LOGGER.warning("Could not attach %s during %s", name, phase, exc_info=True)


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.failed and (driver := item.funcargs.get("driver")) is not None:
        attach_diagnostics(driver, report.when)


@pytest.fixture
def driver(request):
    browser = request.config.getoption("--browser")
    options = webdriver.ChromeOptions() if browser == "chrome" else webdriver.FirefoxOptions()
    if not request.config.getoption("--headed"):
        options.add_argument("--headless=new" if browser == "chrome" else "-headless")
    if binary := request.config.getoption("--browser-binary"):
        options.binary_location = binary
    options.page_load_strategy = "normal"
    service_class = ChromeService if browser == "chrome" else FirefoxService
    kwargs = {"options": options}
    if path := request.config.getoption("--driver-path"):
        kwargs["service"] = service_class(executable_path=path)
    with allure.step(f"Запустить {browser} в отдельном чистом профиле"):
        instance = (webdriver.Chrome if browser == "chrome" else webdriver.Firefox)(**kwargs)

    def close_browser():
        with allure.step("Завершить браузер"):
            instance.quit()

    request.addfinalizer(close_browser)
    # Expose immediately so a later fixture setup failure still gets a screenshot.
    request.node.funcargs["driver"] = instance
    instance.set_page_load_timeout(request.config.getoption("--page-load-timeout"))
    instance.implicitly_wait(0)
    instance.set_window_size(1440, 1100)
    allure.attach(
        json.dumps(instance.capabilities, indent=2),
        "Browser capabilities",
        allure.attachment_type.JSON,
    )
    return instance


def page_factory(page_class, driver, config):
    return page_class(driver, config.getoption("--base-url"), config.getoption("--timeout")).open()


@pytest.fixture
def calendar(driver, pytestconfig):
    return page_factory(CalendarPage, driver, pytestconfig)


@pytest.fixture
def modals(driver, pytestconfig):
    return page_factory(ModalsPage, driver, pytestconfig)


@pytest.fixture
def ads(driver, pytestconfig):
    return page_factory(AdsPage, driver, pytestconfig)


@pytest.fixture
def form_fields(driver, pytestconfig):
    return page_factory(FormFieldsPage, driver, pytestconfig)
