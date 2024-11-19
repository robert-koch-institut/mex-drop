import pathlib
from unittest.mock import AsyncMock, MagicMock, patch

import nest_asyncio
import pytest
from playwright.sync_api import Page, expect

from mex.drop.settings import DropSettings
from mex.drop.state import User
from mex.drop.upload.state import AppState, TempFile

TESTDATA_DIR = pathlib.Path(__file__).parent / "test_files"

nest_asyncio.apply()


@pytest.fixture
def app_state() -> AppState:
    return AppState()


def login(page: Page) -> None:
    page.get_by_placeholder("API key").fill(get_test_key("test"))
    page.get_by_placeholder("X System").fill("test")
    page.get_by_text("Log in").click()


def get_test_key(system: str) -> str:
    settings = DropSettings.get()
    secret_key = [
        key for key, x_sys in settings.drop_api_key_database.items() if system in x_sys
    ]
    if not secret_key:
        msg = f"Test key not found in database: {settings.drop_api_key_database}"
        raise ValueError(msg)
    return secret_key[0].get_secret_value()


def test_cancel_upload(app_state: AppState) -> None:
    app_state.temp_files = [MagicMock(title="file1"), MagicMock(title="file2")]

    app_state.cancel_upload("file1")

    assert len(app_state.temp_files) == 1
    assert app_state.temp_files[0].title == "file2"


@pytest.mark.asyncio(loop_scope="function")
async def test_handle_upload(app_state: AppState) -> None:
    file1 = MagicMock()
    file1.filename = "file1.csv"
    file1.content_type = "text/csv"
    file1.read = AsyncMock(return_value=b"content1")

    file2 = MagicMock()
    file2.filename = "file2.xml"
    file2.content_type = "application/xml"
    file2.read = AsyncMock(return_value=b"content2")

    await app_state.handle_upload([file1, file2])

    assert len(app_state.temp_files) == 2
    assert app_state.temp_files[0].title == "file1.csv"
    assert app_state.temp_files[0].content == b"content1"
    assert app_state.temp_files[1].title == "file2.xml"
    assert app_state.temp_files[1].content == b"content2"


@pytest.mark.asyncio(loop_scope="function")
async def test_handle_upload_duplicate(app_state: AppState) -> None:
    file1 = MagicMock()
    file1.filename = "file1.xml"
    file1.content_type = "application/xml"
    file1.read = AsyncMock(return_value=b"content1")

    app_state.temp_files.append(TempFile(title="file1.xml", content=b"content1"))

    await app_state.handle_upload([file1])

    assert len(app_state.temp_files) == 1


@pytest.mark.asyncio(loop_scope="function")
async def test_submit_data() -> None:
    app_state = AppState(
        user=User(x_system="test_system", api_key=get_test_key("test_system"))
    )
    app_state.temp_files = [TempFile(title="file1.xml", content=b"content1")]

    with (
        patch(
            "mex.drop.upload.state.write_to_file", new_callable=AsyncMock
        ) as mock_write_to_file,
        patch(
            "mex.drop.upload.state.DropSettings.get",
            return_value=MagicMock(drop_directory="/mock/path"),
        ),
        patch("reflex.toast.success") as mock_toast_success,
    ):
        result = await app_state.submit_data()
        mock_write_to_file.assert_called_once_with(
            b"content1", pathlib.Path("/mock/path/test_system/file1.xml")
        )
        assert len(app_state.temp_files) == 0
        mock_toast_success.assert_called_once_with("File upload successful!")
        assert result == mock_toast_success.return_value


@pytest.mark.integration
def test_upload(page: Page) -> None:
    page.goto("http://localhost:3000")
    login(page)
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
def test_empty_upload(page: Page) -> None:
    page.goto("http://localhost:3000")
    login(page)
    page.get_by_text("Submit").click()
    page.screenshot(path="tests_test_main_test_empty_after-submit.jpeg")
    expect(page.locator("text=No files to upload.")).to_be_visible()


@pytest.mark.integration
def test_remove_selected_file(page: Page) -> None:
    page.goto("http://localhost:3000")
    login(page)
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
