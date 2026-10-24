from datetime import date

import allure
import pytest
from selenium.webdriver.common.keys import Keys

pytestmark = [pytest.mark.calendars, allure.feature("Календарь")]


@pytest.mark.positive
@pytest.mark.smoke
@allure.title("CAL-P01..04: Выбор даты через год, месяц и день: {target}")
@pytest.mark.parametrize(
    "target",
    [date(2024, 2, 29), date(2025, 1, 1), date(2025, 12, 31), date(2030, 6, 15)],
    ids=["CAL-P01-leap", "CAL-P02-year-start", "CAL-P03-year-end", "CAL-P04-future"],
)
def test_select_date(calendar, target):
    calendar.select_date(target)
    with allure.step("Проверить точную выбранную дату в формате YYYY-MM-DD"):
        assert calendar.date_value == target.isoformat()


@pytest.mark.positive
@allure.title("CAL-P05: Выбрать сегодняшний день браузера")
def test_select_today(calendar):
    today = date.fromisoformat(
        calendar.driver.execute_script(
            "const d=new Date(); return [d.getFullYear(),String(d.getMonth()+1).padStart(2,'0'),"
            "String(d.getDate()).padStart(2,'0')].join('-')"
        )
    )
    calendar.open_picker()
    calendar.select_day(today.day)
    assert calendar.date_value == today.isoformat()


@pytest.mark.positive
@allure.title("CAL-P06..07: Перелистывание через границу года: {start} → {expected}")
@pytest.mark.parametrize(
    ("start", "direction", "expected"),
    [
        (date(2025, 12, 15), 1, date(2026, 1, 15)),
        (date(2026, 1, 15), -1, date(2025, 12, 15)),
    ],
    ids=["CAL-P06-next-year", "CAL-P07-previous-year"],
)
def test_pagination(calendar, start, direction, expected):
    calendar.enter_date(start.isoformat())
    calendar.open_picker()
    calendar.move_month(direction)
    calendar.select_day(15)
    assert calendar.date_value == expected.isoformat()


@pytest.mark.positive
@allure.title("CAL-P08: Ручной ввод корректной даты")
def test_manual_date(calendar):
    calendar.enter_date("2028-02-29")
    assert calendar.date_value == "2028-02-29"


@pytest.mark.positive
@allure.title("CAL-P09: Повторный выбор заменяет предыдущую дату")
def test_replace_date(calendar):
    calendar.select_date(date(2025, 3, 10))
    calendar.select_date(date(2027, 8, 21))
    assert calendar.date_value == "2027-08-21"


@pytest.mark.positive
@pytest.mark.smoke
@allure.title("CAL-P10: Отправка выбранной даты с подтверждением")
def test_submit_date(calendar):
    calendar.select_date(date(2028, 2, 29))
    calendar.submit()
    assert "Thank you for your response" in calendar.wait_success()


@pytest.mark.negative
@allure.title("CAL-N01: Пустая форма не отправляется")
def test_empty_submission(calendar):
    calendar.submit()
    calendar.assert_stays_hidden(calendar.SUCCESS)
    assert calendar.date_value == ""
    calendar.assert_no_success()


@pytest.mark.negative
@allure.title("CAL-N02: Escape отменяет выбор без изменения даты")
def test_escape_does_not_change_date(calendar):
    calendar.enter_date("2026-10-12")
    calendar.open_picker()
    calendar.move_month(1)
    calendar.visible(calendar.INPUT).send_keys(Keys.ESCAPE)
    calendar.hidden(calendar.PICKER)
    assert calendar.date_value == "2026-10-12"


@pytest.mark.negative
@allure.title("CAL-N03: Нажатие вне календаря не выбирает другую дату")
def test_outside_click_does_not_select(calendar):
    calendar.enter_date("2026-10-12")
    calendar.open_picker()
    calendar.move_month(-1)
    calendar.click(("css selector", "h1"))
    calendar.hidden(calendar.PICKER)
    assert calendar.date_value == "2026-10-12"


@pytest.mark.negative
@allure.title("CAL-N04..05: Некорректная дата отклоняется: {invalid}")
@pytest.mark.parametrize(
    "invalid", ["hello", "2025-02-29"], ids=["CAL-N04-text", "CAL-N05-non-leap-day"]
)
def test_invalid_date(calendar, invalid):
    calendar.enter_date(invalid)
    calendar.submit()
    assert "Please enter a valid date" in calendar.wait_date_error()
    assert calendar.date_value == invalid
    calendar.assert_no_success()
