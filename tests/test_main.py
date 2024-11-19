import pytest
from playwright.sync_api import Page, expect


@pytest.mark.integration
def test_index(page: Page) -> None:
    # load page and check card is visible
    page.goto("http://localhost:3000/login")
    section = page.get_by_test_id("login-card")
    expect(section).to_be_visible()
    page.screenshot(path="tests_test_main_test_index-on-load.jpeg")

    # check logo is visible
    heading = page.get_by_test_id("drop-logo")
    expect(heading).to_be_visible()
