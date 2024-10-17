import pathlib
from unittest.mock import AsyncMock, MagicMock, patch

import nest_asyncio
import pytest

from mex.drop.state import AppState, TempFile


@pytest.fixture
def app_state() -> AppState:
    return AppState()


def test_cancel_upload(app_state: AppState) -> None:
    app_state.temp_files = [MagicMock(title="file1"), MagicMock(title="file2")]

    app_state.cancel_upload("file1")

    assert len(app_state.temp_files) == 1
    assert app_state.temp_files[0].title == "file2"


nest_asyncio.apply()


@pytest.mark.asyncio(loop_scope="function")
async def test_handle_upload(app_state: AppState) -> None:
    file1 = MagicMock()
    file1.filename = "file1.csv"
    file1.read = AsyncMock(return_value=b"content1")

    file2 = MagicMock()
    file2.filename = "file2.xml"
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
    file1.read = AsyncMock(return_value=b"content1")

    app_state.temp_files.append(TempFile(title="file1.xml", content=b"content1"))

    await app_state.handle_upload([file1])

    assert len(app_state.temp_files) == 1


@pytest.mark.asyncio(loop_scope="function")
async def test_submit_data(app_state: AppState) -> None:
    form_data = {"x_system": "system1", "api_token": "token123"}
    app_state.temp_files = [TempFile(title="file1.xml", content=b"content1")]

    with (
        patch(
            "mex.drop.state.get_current_authorized_x_systems", return_value=["system1"]
        ),
        patch("mex.drop.state.is_authorized", return_value=True),
        patch(
            "mex.drop.state.write_to_file", new_callable=AsyncMock
        ) as mock_write_to_file,
        patch(
            "mex.drop.state.DropSettings.get",
            return_value=MagicMock(drop_directory="/mock/path"),
        ),
    ):
        await app_state.submit_data(form_data=form_data)

        mock_write_to_file.assert_called_once_with(
            b"content1", pathlib.Path("/mock/path/system1/file1.xml")
        )
        assert len(app_state.temp_files) == 0
