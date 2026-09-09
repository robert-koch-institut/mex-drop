from collections.abc import Callable

import pytest

from mex.drop.models import User
from mex.drop.state import State


def test_default_locale_is_german(drop_state: State) -> None:
    assert drop_state.current_locale == "de"


def test_change_locale(drop_state: State) -> None:
    drop_state.change_locale("en")  # type: ignore[operator]

    assert drop_state.current_locale == "en"


@pytest.mark.parametrize(
    ("locale_id", "expected_titles"),
    [
        pytest.param("de", ["Hochladen", "Durchsuchen"], id="de"),
        pytest.param("en", ["Upload", "Browse"], id="en"),
    ],
)
def test_nav_items_translated(
    drop_state: State, locale_id: str, expected_titles: list[str]
) -> None:
    drop_state.change_locale(locale_id)  # type: ignore[operator]

    assert [item.title for item in drop_state.nav_items_translated] == expected_titles


def test_nav_items_translated_keeps_routes(drop_state: State) -> None:
    assert [item.raw_path for item in drop_state.nav_items_translated] == [
        "/",
        "/browse",
    ]
    assert [item.route_ids for item in drop_state.nav_items_translated] == [
        ["/", "/index"],
        ["/browse"],
    ]


def test_nav_items_translated_reflects_active_flag(drop_state: State) -> None:
    drop_state._nav_items[1].active = True

    assert [item.active for item in drop_state.nav_items_translated] == [False, True]


@pytest.mark.parametrize(
    ("locale_id", "expected_label"),
    [
        pytest.param("de", "Abmelden", id="de"),
        pytest.param("en", "Logout", id="en"),
    ],
)
def test_label_nav_bar_logout_button(
    drop_state: State, locale_id: str, expected_label: str
) -> None:
    drop_state.change_locale(locale_id)  # type: ignore[operator]

    assert drop_state.label_nav_bar_logout_button == expected_label


def test_locale_service_lookup_follows_current_locale(drop_state: State) -> None:
    """The states resolve their runtime strings through `_locale_service`."""
    label_id = "upload.submit_button"
    lookup = drop_state._locale_service.get_ui_label

    assert lookup(drop_state.current_locale, label_id) == "Absenden"

    drop_state.change_locale("en")  # type: ignore[operator]

    assert lookup(drop_state.current_locale, label_id) == "Submit"


def test_logout_keeps_the_chosen_locale(
    drop_state: State,
    get_test_key: Callable[[str], str],
) -> None:
    """`reset` would clear `current_locale` too, so `logout` has to restore it."""
    drop_state.user = User(x_system="test_system", api_key=get_test_key("test_system"))
    drop_state.change_locale("en")  # type: ignore[operator]

    drop_state.logout()  # type: ignore[operator]

    assert drop_state.user is None
    assert drop_state.current_locale == "en"
