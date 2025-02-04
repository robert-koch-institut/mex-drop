import pytest
from playwright.sync_api import Page, expect


@pytest.mark.integration
def test_login_page(page: Page, get_test_key) -> None:
    page.goto("http://localhost:3000")
    page.get_by_placeholder("API Key").fill(get_test_key("test"))
    page.get_by_placeholder("X-System").fill("test")
    page.screenshot(path="tests_test_login_test_login_success.jpeg")

    page.get_by_text("Log in").click()
    expect(page.locator("text=Logout")).to_be_visible()
    page.screenshot(path="tests_test_login_test_login_success_after.jpeg")

    page.get_by_text("Logout").click()
    expect(page.locator("text=Log in")).to_be_visible()
