from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest

from mex.drop.file_history.state import ListState
from mex.drop.state import State


@pytest.fixture
def setup_list_state(app_state: State) -> ListState:
    """Fixture to set up ListState with a mock user."""
    return ListState(parent_state=app_state)


@patch("mex.drop.file_history.state.pathlib.Path")
@patch("mex.drop.file_history.state.DropSettings.get")
@patch("mex.drop.file_history.state.rx.toast.error")
def test_refresh_missing_directory(
    mock_toast_error, mock_drop_settings_get, mock_path, setup_list_state
):
    """Test the case where the x-system directory does not exist."""
    state = setup_list_state

    mock_settings = MagicMock()
    mock_settings.drop_directory = "/mock/drop/directory"
    mock_drop_settings_get.return_value = mock_settings

    mock_x_system_dir = mock_path.return_value
    mock_x_system_dir.is_dir.return_value = False

    state.refresh()

    mock_toast_error.assert_called_once_with(
        "The requested x-system was not found on this server.", close_button=True
    )


@patch("mex.drop.file_history.state.pathlib.Path")
@patch("mex.drop.file_history.state.DropSettings.get")
def test_refresh_success(mock_drop_settings_get, mock_path, setup_list_state):
    """Test successful retrieval of uploaded files."""
    state = setup_list_state

    mock_settings = MagicMock()
    mock_settings.drop_directory = "/mock/drop/directory"
    mock_drop_settings_get.return_value = mock_settings

    mock_x_system_dir = mock_path.return_value
    mock_x_system_dir.is_dir.return_value = True

    mock_file = MagicMock()
    mock_file.is_file.return_value = True
    mock_file.name = "test_file.csv"
    mock_file.stat.return_value.st_ctime = 1680000000
    mock_file.stat.return_value.st_mtime = 1680001000

    mock_x_system_dir.glob.return_value = [mock_file]

    state.refresh()

    expected_file_list = [
        {
            "name": "test_file.csv",
            "created": datetime.fromtimestamp(1680000000, tz=UTC).strftime(
                "%d-%m-%Y %H:%M:%S"
            ),
            "modified": datetime.fromtimestamp(1680001000, tz=UTC).strftime(
                "%d-%m-%Y %H:%M:%S"
            ),
        }
    ]
    assert state.file_list == expected_file_list
