import polib
import pytest

from mex.drop.locale_service import LocaleService


def test_get_available_locales() -> None:
    locale_service = LocaleService.get()

    locales = locale_service.get_available_locales()

    assert [(locale.id, locale.label, locale.code) for locale in locales] == [
        ("de", "Deutsch", "DEU"),
        ("en", "English", "ENG"),
    ]


def test_get_available_locales_values() -> None:
    locale_service = LocaleService.get()

    locale = locale_service.get_available_locales()[0]

    assert list(locale.values()) == ["de", "Deutsch", "de", "DEU"]


@pytest.mark.parametrize(
    ("locale_id", "msg_id", "expected_label"),
    [
        pytest.param(
            "de", "layout.nav_bar.browse_navitem", "Durchsuchen", id="de:nav_browse"
        ),
        pytest.param(
            "en", "layout.nav_bar.browse_navitem", "Browse", id="en:nav_browse"
        ),
        pytest.param(
            "de", "layout.nav_bar.logout_button", "Abmelden", id="de:nav_logout"
        ),
        pytest.param(
            "en", "layout.nav_bar.logout_button", "Logout", id="en:nav_logout"
        ),
        pytest.param("de", "login.button_login", "Anmelden", id="de:login_button"),
        pytest.param("en", "login.button_login", "Login", id="en:login_button"),
        pytest.param("de", "upload.submit_button", "Absenden", id="de:upload_submit"),
        pytest.param("en", "upload.submit_button", "Submit", id="en:upload_submit"),
        # an unknown msg_id falls back to the msg_id itself, like plain gettext
        pytest.param("de", "not.a.known.label", "not.a.known.label", id="de:unknown"),
        pytest.param("en", "not.a.known.label", "not.a.known.label", id="en:unknown"),
    ],
)
def test_get_ui_label(locale_id: str, msg_id: str, expected_label: str) -> None:
    locale_service = LocaleService.get()

    assert locale_service.get_ui_label(locale_id, msg_id) == expected_label


@pytest.mark.parametrize(
    ("locale_id", "msg_id", "arg", "expected_label"),
    [
        pytest.param(
            "de",
            "upload.file_removed.format",
            "test.csv",
            "Datei test.csv aus dem Upload entfernt.",
            id="de:file_removed",
        ),
        pytest.param(
            "en",
            "upload.file_removed.format",
            "test.csv",
            "File test.csv removed from upload.",
            id="en:file_removed",
        ),
    ],
)
def test_get_ui_label_with_format_args(
    locale_id: str, msg_id: str, arg: str, expected_label: str
) -> None:
    locale_service = LocaleService.get()

    label = locale_service.get_ui_label(locale_id, msg_id).format(arg)

    assert label == expected_label


def test_get_ui_label_unknown_locale_raises() -> None:
    locale_service = LocaleService.get()

    with pytest.raises(ValueError, match=r"'locale_id' \(fr\) is not valid"):
        locale_service.get_ui_label("fr", "layout.nav_bar.logout_button")


def test_all_locales_define_the_same_msg_ids() -> None:
    """Every catalog must translate every msg_id, so no locale falls back silently."""
    locale_service = LocaleService.get()

    msg_ids = {
        locale.id: {
            entry.msgid
            for entry in polib.pofile(
                locale_service._drop_locale_path / f"{locale.id}.po"
            )
        }
        for locale in locale_service.get_available_locales()
    }

    assert msg_ids["de"] == msg_ids["en"]
    assert "layout.nav_bar.browse_navitem" in msg_ids["de"]
