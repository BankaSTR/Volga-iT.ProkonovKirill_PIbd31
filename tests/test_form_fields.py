import allure
import pytest

pytestmark = [pytest.mark.form_fields, allure.feature("Automation Tools → Message")]


@pytest.mark.positive
@pytest.mark.smoke
@allure.title("FORM-P01: Selenium читает Automation Tools и заполняет Message через запятую")
def test_tools_to_message(form_fields):
    tools = form_fields.automation_tools()
    with allure.step("Проверить, что список непустой и каждое название прочитано"):
        assert tools
        assert all(tools)
        assert len(tools) == len(set(tools))
    text = form_fields.fill_tools_message(tools)
    allure.attach("\n".join(tools), "Automation Tools из DOM", allure.attachment_type.TEXT)
    assert form_fields.value(form_fields.MESSAGE) == ", ".join(tools)
    assert text == form_fields.value(form_fields.MESSAGE)
    assert "Message received!" in form_fields.submit()
