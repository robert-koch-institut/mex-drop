from collections.abc import Callable
from unittest.mock import Mock

import pytest
from pytest import MonkeyPatch

from mex.drop.locale_service import LocaleService
from mex.drop.login.state import LoginState
from mex.drop.state import State


@pytest.fixture
def login_state(drop_state: State) -> LoginState:
    """Fixture to set up LoginState below a properly mounted root state."""
    return LoginState(parent_state=drop_state, api_key="", x_system="")


@pytest.mark.parametrize(
    ("locale_id", "expected_message"),
    [
        pytest.param("de", "Bitte geben Sie Ihren API-Schlüssel ein.", id="de"),
        pytest.param("en", "Please enter your API Key.", id="en"),
    ],
)
def test_login_without_api_key(
    login_state: LoginState,
    monkeypatch: MonkeyPatch,
    locale_id: str,
    expected_message: str,
) -> None:
    mock_toast_error = Mock()
    monkeypatch.setattr("mex.drop.login.state.rx.toast.error", mock_toast_error)
    login_state.change_locale(locale_id)  # type: ignore[operator]
    login_state.api_key = ""

    login_state.login()  # type: ignore[operator]

    mock_toast_error.assert_called_once_with(expected_message)
    assert login_state.user is None


@pytest.mark.parametrize(
    ("locale_id", "expected_message"),
    [
        pytest.param("de", "Ungültiger API-Schlüssel.", id="de"),
        pytest.param("en", "Invalid API Key.", id="en"),
    ],
)
def test_login_with_unknown_api_key(
    login_state: LoginState,
    monkeypatch: MonkeyPatch,
    locale_id: str,
    expected_message: str,
) -> None:
    mock_toast_error = Mock()
    monkeypatch.setattr("mex.drop.login.state.rx.toast.error", mock_toast_error)
    login_state.change_locale(locale_id)  # type: ignore[operator]
    login_state.api_key = "not-a-known-key"
    login_state.x_system = "test_system"

    login_state.login()  # type: ignore[operator]

    mock_toast_error.assert_called_once_with(expected_message)
    assert login_state.user is None


def test_login_with_unauthorized_x_system(
    login_state: LoginState,
    monkeypatch: MonkeyPatch,
    get_test_key: Callable[[str], str],
) -> None:
    mock_toast_error = Mock()
    monkeypatch.setattr("mex.drop.login.state.rx.toast.error", mock_toast_error)
    login_state.api_key = get_test_key("test_system")
    login_state.x_system = "foo_system"

    login_state.login()  # type: ignore[operator]

    mock_toast_error.assert_called_once_with(
        LocaleService.get().get_ui_label("de", "login.invalid_credentials")
    )
    assert login_state.user is None


def test_login_success(
    login_state: LoginState,
    get_test_key: Callable[[str], str],
) -> None:
    login_state.api_key = get_test_key("test_system")
    login_state.x_system = "test_system"

    login_state.login()  # type: ignore[operator]

    assert login_state.user is not None
    assert login_state.user.x_system == "test_system"


def test_login_raises_only_for_unexpected_errors(
    login_state: LoginState,
    monkeypatch: MonkeyPatch,
) -> None:
    """Anything other than a 401 still reaches the backend exception handler."""

    def raise_unexpected(api_key: str) -> None:
        raise RuntimeError(api_key)

    monkeypatch.setattr(
        "mex.drop.login.state.get_current_authorized_x_systems", raise_unexpected
    )
    login_state.api_key = "any-key"

    with pytest.raises(RuntimeError):
        login_state.login()  # type: ignore[operator]
