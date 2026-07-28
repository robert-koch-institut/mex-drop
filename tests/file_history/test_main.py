from collections.abc import Callable

import pytest
from playwright.sync_api import Page, expect

from tests.conftest import TESTDATA_DIR


def upload_file(page: Page) -> None:
    with page.expect_file_chooser() as fc_info:
        page.locator("role=button[name='Select Files']").click()
    file_chooser = fc_info.value
    file_chooser.set_files(
        str(TESTDATA_DIR / "test.csv"),
    )
    page.get_by_text("Submit").click()


def login(page: Page, api_key: str, x_system: str) -> None:
    page.get_by_placeholder("API Key").fill(api_key)
    page.get_by_placeholder("X-System").fill(x_system)
    page.get_by_test_id("login-button").click()


def logout(page: Page) -> None:
    page.get_by_test_id("user-menu").click()
    page.get_by_test_id("logout-button").click()


@pytest.mark.integration
def test_upload(
    page: Page,
    get_test_key: Callable[[str], str],
    base_url: str,
) -> None:
    page.goto(base_url)
    login(page, get_test_key("test"), "test")
    upload_file(page)

    page.get_by_text("File History").click()
    expect(page.get_by_text("test.csv")).to_be_visible()
    page.screenshot(path="tests_history_main_test_upload.png")

    # the file history is scoped to the x-system of the logged-in user
    logout(page)
    login(page, get_test_key("other"), "other")
    page.get_by_text("File History").click()
    expect(page.get_by_text("test.csv")).not_to_be_visible()
    page.screenshot(path="tests_history_main_test_upload_after_reload.png")
