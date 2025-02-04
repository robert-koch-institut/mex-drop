import pathlib

import pytest
from playwright.sync_api import Page, expect

from mex.drop.settings import DropSettings
from tests.conftest import TESTDATA_DIR


def login(page: Page, get_test_key) -> None:
    page.get_by_placeholder("API key").fill(get_test_key("test"))
    page.get_by_placeholder("X-System").fill("test")
    page.get_by_text("Log in").click()


@pytest.mark.integration
def test_upload(page: Page, get_test_key) -> None:
    page.goto("http://localhost:3000")
    login(page, get_test_key)
    with page.expect_file_chooser() as fc_info:
        page.locator("role=button[name='Select Files']").click()
    file_chooser = fc_info.value
    file_chooser.set_files(
        str(TESTDATA_DIR / "test.csv"),
    )

    expect(page.get_by_text("test.csv")).to_be_visible()
    page.screenshot(path="tests_test_main_test_index-after-select.jpeg")

    page.get_by_text("Submit").click()
    page.screenshot(path="tests_test_main_test_index-after-submit.jpeg")

    expect(page.get_by_text("test.csv")).not_to_be_visible()

    settings = DropSettings.get()
    expected_file = pathlib.Path(settings.drop_directory, "test", "test.csv")
    assert expected_file.read_text() == (TESTDATA_DIR / "test.csv").read_text()


@pytest.mark.integration
def test_empty_upload(page: Page, get_test_key) -> None:
    page.goto("http://localhost:3000")
    login(page, get_test_key)
    page.get_by_text("Submit").click()
    page.screenshot(path="tests_test_main_test_empty_after-submit.jpeg")
    expect(page.locator("text=No files to upload.")).to_be_visible()


@pytest.mark.integration
def test_remove_selected_file(page: Page, get_test_key) -> None:
    page.goto("http://localhost:3000")
    login(page, get_test_key)
    with page.expect_file_chooser() as fc_info:
        page.locator("role=button[name='Select Files']").click()
    file_chooser = fc_info.value
    file_chooser.set_files(
        str(TESTDATA_DIR / "test.xml"),
    )

    expect(page.get_by_text("test.xml")).to_be_visible()
    page.screenshot(path="tests_test_main_test_index-after-select2.jpeg")
    page.get_by_role("button").and_(page.get_by_title("remove file")).click()
    page.screenshot(path="tests_test_main_test_index-after-delete.jpeg")

    expect(page.get_by_text("test.xml")).not_to_be_visible()
