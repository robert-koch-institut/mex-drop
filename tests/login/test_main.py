from collections.abc import Callable

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.integration
def test_login_page(
    page: Page,
    get_test_key: Callable[[str], str],
    base_url: str,
) -> None:
    page.goto(base_url)
    page.get_by_placeholder("X-System").fill("test")
    page.get_by_placeholder("API Key").fill(get_test_key("test"))
    page.screenshot(path="tests_test_login_test_login_page_filled.png")

    page.get_by_test_id("login-button").click()
    expect(page.get_by_test_id("nav-bar")).to_be_visible()
    page.screenshot(path="tests_test_login_test_login_page_after.png")

    page.get_by_test_id("user-menu").click()
    expect(page.locator("text=Logout")).to_be_visible()
    page.get_by_text("Logout").click()
    expect(page.get_by_test_id("login-button")).to_be_visible()


@pytest.mark.integration
def test_login_page_with_enter_key(
    page: Page,
    get_test_key: Callable[[str], str],
    base_url: str,
) -> None:
    page.goto(base_url)
    page.get_by_placeholder("X-System").fill("test")
    page.get_by_placeholder("API Key").fill(get_test_key("test"))
    page.screenshot(path="tests_test_login_test_login_page_with_enter_key_filled.png")

    page.get_by_test_id("login-button").click()
    expect(page.get_by_test_id("nav-bar")).to_be_visible()
    page.screenshot(path="tests_test_login_test_login_page_with_enter_key_after.png")

    page.get_by_test_id("user-menu").click()
    expect(page.locator("text=Logout")).to_be_visible()
    page.get_by_text("Logout").click()
    expect(page.get_by_test_id("login-button")).to_be_visible()
