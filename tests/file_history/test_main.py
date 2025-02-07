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


def login(page: Page, get_test_key) -> None:
    page.get_by_placeholder("API Key").fill(get_test_key("test"))
    page.get_by_placeholder("X-System").fill("test")
    page.get_by_test_id("login-button").click()


@pytest.mark.integration
def test_upload(page: Page, get_test_key, clean_test_directory) -> None:
    page.goto("http://localhost:3000")
    clean_test_directory()
    login(page, get_test_key)
    upload_file(page)

    page.get_by_text("File History").click()
    expect(page.get_by_text("test.csv")).to_be_visible()
    page.screenshot(path="tests_history_main_test_upload.jpeg")

    clean_test_directory()
    page.reload()
    expect(page.get_by_text("test.csv")).not_to_be_visible()
    page.screenshot(path="tests_history_main_test_upload_after_reload.jpeg")
