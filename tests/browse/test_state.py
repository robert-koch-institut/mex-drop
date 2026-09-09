from datetime import UTC, datetime
from unittest.mock import Mock

import pytest
from pytest import MonkeyPatch

from mex.drop.browse.models import FileDetails
from mex.drop.browse.state import BrowseState
from mex.drop.locale_service import LocaleService
from mex.drop.settings import DropSettings
from mex.drop.state import State


@pytest.fixture
def browse_state(app_state: State) -> BrowseState:
    """Fixture to set up BrowseState with a mock user."""
    return BrowseState(parent_state=app_state)


def test_refresh_missing_directory(
    browse_state: BrowseState,
    monkeypatch: MonkeyPatch,
) -> None:
    """Test the case where the x-system directory does not exist."""
    mock_toast_error = Mock()
    monkeypatch.setattr("mex.drop.browse.state.rx.toast.error", mock_toast_error)

    browse_state.refresh()  # type: ignore[operator]

    mock_toast_error.assert_called_once_with(
        LocaleService.get().get_ui_label("de", "browse.x_system_not_found"),
        close_button=True,
    )

    assert browse_state.file_list == []


def test_refresh_success(settings: DropSettings, browse_state: BrowseState) -> None:
    """Test successful retrieval of uploaded files."""
    mock_x_system_dir = settings.drop_directory / "test_system"
    mock_x_system_dir.mkdir(parents=True)

    mock_file = mock_x_system_dir / "test_file.csv"
    mock_file.touch()

    browse_state.refresh()  # type: ignore[operator]

    expected_file_list = [
        FileDetails(
            name="test_file.csv",
            created=datetime.fromtimestamp(mock_file.stat().st_ctime, tz=UTC).strftime(
                "%d-%m-%Y %H:%M:%S"
            ),
            modified=datetime.fromtimestamp(mock_file.stat().st_mtime, tz=UTC).strftime(
                "%d-%m-%Y %H:%M:%S"
            ),
        )
    ]
    assert browse_state.file_list == expected_file_list
