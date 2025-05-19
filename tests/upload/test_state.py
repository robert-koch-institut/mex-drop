import pathlib
from unittest.mock import AsyncMock, MagicMock, patch

import nest_asyncio
import pytest

from mex.drop.state import State
from mex.drop.upload.models import TempFile
from mex.drop.upload.state import UploadState

nest_asyncio.apply()


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
def upload_state(app_state: State) -> UploadState:
    """Fixture to set up UploadState with a mock user."""
    return UploadState(parent_state=app_state)


def test_cancel_upload(upload_state: UploadState) -> None:
    upload_state.temp_files = [MagicMock(title="file1"), MagicMock(title="file2")]

    upload_state.cancel_upload("file1")

    assert len(upload_state.temp_files) == 1
    assert upload_state.temp_files[0].title == "file2"


@pytest.mark.anyio
async def test_handle_upload(upload_state: UploadState) -> None:
    file1 = MagicMock()
    file1.filename = "file1.csv"
    file1.content_type = "text/csv"
    file1.read = AsyncMock(return_value=b"content1")

    file2 = MagicMock()
    file2.filename = "file2.xml"
    file2.content_type = "application/xml"
    file2.read = AsyncMock(return_value=b"content2")

    await upload_state.handle_upload([file1, file2])

    assert len(upload_state.temp_files) == 2
    assert upload_state.temp_files[0].title == "file1.csv"
    assert upload_state.temp_files[0].content == b"content1"
    assert upload_state.temp_files[1].title == "file2.xml"
    assert upload_state.temp_files[1].content == b"content2"


@pytest.mark.anyio
async def test_handle_upload_duplicate(upload_state: UploadState) -> None:
    file1 = MagicMock()
    file1.filename = "file1.xml"
    file1.content_type = "application/xml"
    file1.read = AsyncMock(return_value=b"content1")

    upload_state.temp_files.append(TempFile(title="file1.xml", content=b"content1"))

    await upload_state.handle_upload([file1])

    assert len(upload_state.temp_files) == 1


@pytest.mark.anyio
async def test_submit_data(upload_state: UploadState) -> None:
    upload_state.temp_files = [TempFile(title="file1.xml", content=b"content1")]

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
        result = await upload_state.submit_data()
        mock_write_to_file.assert_called_once_with(
            b"content1", pathlib.Path("/mock/path/test_system/file1.xml")
        )
        assert len(upload_state.temp_files) == 0
        mock_toast_success.assert_called_once_with("File upload successful!")
        assert result == mock_toast_success.return_value
