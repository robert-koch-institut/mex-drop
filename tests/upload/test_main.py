import pathlib
from collections.abc import Callable

import pytest
from playwright.sync_api import Page, expect

from mex.drop.settings import DropSettings
from tests.conftest import TESTDATA_DIR


@pytest.fixture
def upload_page(
    page: Page,
    frontend_url: str,
    get_test_key: Callable[[str], str],
) -> Page:
    page.goto(frontend_url)
    page.get_by_placeholder("API Key").fill(get_test_key("test"))
    page.get_by_placeholder("X-System").fill("test")
    page.get_by_test_id("login-button").click()
    return page


@pytest.mark.integration
def test_upload(upload_page: Page) -> None:
    page = upload_page
    with page.expect_file_chooser() as fc_info:
        page.locator("role=button[name='Select Files']").click()
    file_chooser = fc_info.value
    file_chooser.set_files(str(TESTDATA_DIR / "test.csv"))

    expect(page.get_by_text("test.csv")).to_be_visible()
    page.screenshot(path="tests_test_main_test_index-after-select.png")

    page.get_by_text("Submit").click()
    page.screenshot(path="tests_test_main_test_index-after-submit.png")

    expect(page.get_by_text("test.csv")).not_to_be_visible()

    settings = DropSettings.get()
    expected_file = pathlib.Path(settings.drop_directory, "test", "test.csv")
    assert expected_file.read_text() == (TESTDATA_DIR / "test.csv").read_text()


@pytest.mark.integration
def test_empty_upload(upload_page: Page) -> None:
    page = upload_page
    page.get_by_text("Submit").click()
    page.screenshot(path="tests_test_main_test_empty_after-submit.png")
    expect(page.locator("text=No files to upload.")).to_be_visible()


@pytest.mark.integration
def test_remove_selected_file(upload_page: Page) -> None:
    page = upload_page
    with page.expect_file_chooser() as fc_info:
        page.locator("role=button[name='Select Files']").click()
    file_chooser = fc_info.value
    file_chooser.set_files(str(TESTDATA_DIR / "test.xml"))

    expect(page.get_by_text("test.xml")).to_be_visible()
    page.screenshot(path="tests_test_main_test_index-after-select2.png")
    page.get_by_role("button").and_(page.get_by_title("remove file")).click()
    page.screenshot(path="tests_test_main_test_index-after-delete.png")

    expect(page.get_by_text("test.xml")).not_to_be_visible()
