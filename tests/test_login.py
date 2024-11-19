import pytest
from playwright.sync_api import Page, expect

from mex.drop.login.state import LoginState
from mex.drop.settings import DropSettings
from mex.drop.state import State


def get_test_key(x_system: str) -> str:
    settings = DropSettings.get()
    secret_key = [
        key
        for key, x_sys in settings.drop_api_key_database.items()
        if x_system in x_sys
    ]
    if not secret_key:
        msg = f"Test key not found in database: {settings.drop_api_key_database}"
        raise ValueError(msg)
    return secret_key[0].get_secret_value()


@pytest.mark.integration
def test_login_page(page: Page) -> None:
    page.goto("http://localhost:3000")
    page.get_by_placeholder("API Key").fill(get_test_key("test"))
    page.get_by_placeholder("X System").fill("test")
    page.screenshot(path="tests_test_login_test_login_success.jpeg")

    page.get_by_text("Log in").click()
    expect(page.locator("text=Logout")).to_be_visible()
    page.screenshot(path="tests_test_login_test_login_success_after.jpeg")

    page.get_by_text("Logout").click()
    expect(page.locator("text=Log in")).to_be_visible()


def test_login_user_and_logout() -> None:
    login_state = LoginState(
        api_key=get_test_key("test_system"),
        x_system="test_system",
        parent_state=State(),
    )
    assert "/" in str(login_state.login_user())
    assert login_state.user
    assert login_state.user.x_system == "test_system"
    assert login_state.user.api_key == get_test_key("test_system")

    login_state.logout()
    assert login_state.user is None


def test_login_user_fail() -> None:
    login_state = LoginState(
        api_key=get_test_key("test_system"), x_system="wrong_sys", parent_state=State()
    )
    login_state.login_user()
    assert login_state.user is None
