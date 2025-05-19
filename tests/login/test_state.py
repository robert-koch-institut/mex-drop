from collections.abc import Callable

from mex.drop.login.state import LoginState
from mex.drop.state import State


def test_login_and_logout(get_test_key: Callable[[str], str]) -> None:
    login_state = LoginState(
        api_key=get_test_key("test_system"),
        x_system="test_system",
        parent_state=State(),
    )
    assert "/" in str(login_state.login())
    assert login_state.user
    assert login_state.user.x_system == "test_system"
    assert login_state.user.api_key == get_test_key("test_system")

    login_state.logout()
    assert login_state.user is None


def test_login_fail(get_test_key: Callable[[str], str]) -> None:
    login_state = LoginState(
        api_key=get_test_key("test_system"), x_system="wrong_sys", parent_state=State()
    )
    login_state.login()
    assert login_state.user is None
