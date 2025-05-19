from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import Mock

import pytest
from pytest import MonkeyPatch

from mex.drop.file_history.state import ListState
from mex.drop.settings import DropSettings
from mex.drop.state import State


@pytest.fixture
def list_state(app_state: State) -> ListState:
    """Fixture to set up ListState with a mock user."""
    return ListState(parent_state=app_state)


def test_refresh_missing_directory(
    list_state: ListState,
    tmp_path: Path,
    settings: DropSettings,
    monkeypatch: MonkeyPatch,
) -> None:
    """Test the case where the x-system directory does not exist."""
    settings.drop_directory = tmp_path
    mock_toast_error = Mock()
    monkeypatch.setattr("mex.drop.file_history.state.rx.toast.error", mock_toast_error)

    list_state.refresh()

    mock_toast_error.assert_called_once_with(
        "The requested x-system was not found on this server.", close_button=True
    )

    assert list_state.file_list == []


def test_refresh_success(
    settings: DropSettings, list_state: ListState, tmp_path: Path
) -> None:
    """Test successful retrieval of uploaded files."""
    settings.drop_directory = tmp_path

    mock_x_system_dir = settings.drop_directory / "test_system"
    mock_x_system_dir.mkdir()

    mock_file = mock_x_system_dir / "test_file.csv"
    mock_file.touch()

    list_state.refresh()

    expected_file_list = [
        {
            "name": "test_file.csv",
            "created": datetime.fromtimestamp(
                mock_file.stat().st_ctime, tz=UTC
            ).strftime("%d-%m-%Y %H:%M:%S"),
            "modified": datetime.fromtimestamp(
                mock_file.stat().st_mtime, tz=UTC
            ).strftime("%d-%m-%Y %H:%M:%S"),
        }
    ]
    assert list_state.file_list == expected_file_list
