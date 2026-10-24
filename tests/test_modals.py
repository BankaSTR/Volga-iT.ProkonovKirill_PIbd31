import allure
import pytest

pytestmark = [pytest.mark.modals, allure.feature("Модальные окна")]


@pytest.mark.positive
@pytest.mark.smoke
@allure.title("MOD-P01: Простое окно показывает правильный заголовок и текст")
def test_simple_content(modals):
    dialog = modals.open_simple()
    assert dialog.title == "Simple Modal"
    assert dialog.content == "Hi, I’m a simple modal."
    modals.form.assert_closed()


@pytest.mark.positive
@allure.title("MOD-P02: Закрыть простое окно крестиком и открыть повторно")
def test_simple_reopen(modals):
    dialog = modals.open_simple()
    dialog.close()
    dialog.assert_closed()
    modals.open_simple()
    assert dialog.title == "Simple Modal"


@pytest.mark.positive
@allure.title("MOD-P03: Закрыть простое окно с клавиатуры")
def test_simple_keyboard_close(modals):
    dialog = modals.open_simple()
    dialog.close_with_keyboard()
    dialog.assert_closed()


@pytest.mark.positive
@allure.title("MOD-P04: Открыть форму с пустыми полями и обязательным Name")
def test_form_initial_state(modals):
    dialog = modals.open_form()
    assert dialog.title == "Modal Containing A Form"
    for field in ("name", "email", "message"):
        assert modals.value(modals.field(field)) == ""
    assert modals.visible(modals.field("name")).get_property("required")
    assert not modals.visible(modals.field("email")).get_property("required")
    modals.simple.assert_closed()


@pytest.mark.positive
@allure.title("MOD-P05: Закрыть форму с помощью Escape")
def test_form_escape(modals):
    dialog = modals.open_form()
    dialog.escape()
    dialog.assert_closed()


@pytest.mark.positive
@allure.title("MOD-P06: Закрытие и повторное открытие сохраняют введённые данные")
def test_form_reopen_preserves_data(modals):
    dialog = modals.open_form()
    modals.fill_form(message="Проверка Volga IT")
    dialog.close()
    modals.open_form()
    assert modals.value(modals.field("name")) == "Volga IT"
    assert modals.value(modals.field("email")) == "volga.it@example.com"
    assert modals.value(modals.field("message")) == "Проверка Volga IT"


@pytest.mark.positive
@pytest.mark.smoke
@allure.title("MOD-P07: Отправить заполненную контактную форму")
def test_submit_full_form(modals):
    modals.open_form()
    modals.fill_form(message="Volga IT UI automation")
    modals.submit()
    assert "Thank you for your response" in modals.wait_success()


@pytest.mark.positive
@allure.title("MOD-P08: Отправить только обязательное имя")
def test_submit_required_only(modals):
    modals.open_form()
    modals.fill_form(name="Кирилл Проконов", email="")
    modals.submit()
    assert "Thank you for your response" in modals.wait_success()


@pytest.mark.positive
@allure.title("MOD-P09: Исправление некорректного email позволяет отправить форму")
def test_recover_from_invalid_email(modals):
    modals.open_form()
    modals.fill_form(email="invalid-email", message="Keep this message")
    modals.submit()
    assert "valid email" in modals.field_error("email").lower()
    modals.fill(modals.field("email"), "corrected@example.com")
    assert modals.value(modals.field("message")) == "Keep this message"
    modals.submit()
    assert "Thank you for your response" in modals.wait_success()


@pytest.mark.negative
@allure.title("MOD-N01: Пустое имя блокирует отправку и сохраняет другие поля")
def test_missing_name(modals):
    modals.open_form()
    modals.fill_form(name="", message="Keep this text")
    modals.submit()
    assert "required" in modals.field_error("name").lower()
    assert modals.value(modals.field("message")) == "Keep this text"
    modals.assert_no_success()


@pytest.mark.negative
@allure.title("MOD-N02..03: Некорректный email блокирует отправку: {email}")
@pytest.mark.parametrize(
    "email", ["invalid-email", "user@"], ids=["MOD-N02-no-at", "MOD-N03-no-domain"]
)
def test_invalid_email(modals, email):
    modals.open_form()
    modals.fill_form(email=email)
    modals.submit()
    assert "valid email" in modals.field_error("email").lower()
    assert modals.value(modals.field("email")) == email
    modals.assert_no_success()


@pytest.mark.negative
@allure.title("MOD-N04: Escape не закрывает простое окно")
def test_simple_ignores_escape(modals):
    dialog = modals.open_simple()
    dialog.escape()
    dialog.assert_open()
    dialog.close()
