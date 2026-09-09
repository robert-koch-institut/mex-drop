from collections.abc import Callable

import pytest
from playwright.sync_api import Page, expect

from mex.drop.locale_service import LocaleService
from tests.conftest import build_ui_label_regex


@pytest.mark.integration
def test_login_page(
    page: Page,
    get_test_key: Callable[[str], str],
    base_url: str,
) -> None:
    page.goto(base_url)
    page.get_by_test_id("input-x-system").fill("test")
    page.get_by_test_id("input-api-key").fill(get_test_key("test"))
    page.screenshot(path="tests_test_login_test_login_page_filled.png")

    page.get_by_test_id("login-button").click()
    expect(page.get_by_test_id("nav-bar")).to_be_visible()
    page.screenshot(path="tests_test_login_test_login_page_after.png")

    page.get_by_test_id("user-menu").click()
    logout_button = page.get_by_test_id("logout-button")
    expect(logout_button).to_have_text(
        build_ui_label_regex("layout.nav_bar.logout_button")
    )
    logout_button.click()
    expect(page.get_by_test_id("login-button")).to_be_visible()


@pytest.mark.integration
def test_login_page_with_enter_key(
    page: Page,
    get_test_key: Callable[[str], str],
    base_url: str,
) -> None:
    page.goto(base_url)
    page.get_by_test_id("input-x-system").fill("test")
    page.get_by_test_id("input-api-key").fill(get_test_key("test"))
    page.screenshot(path="tests_test_login_test_login_page_with_enter_key_filled.png")

    page.get_by_test_id("login-button").click()
    expect(page.get_by_test_id("nav-bar")).to_be_visible()
    page.screenshot(path="tests_test_login_test_login_page_with_enter_key_after.png")

    page.get_by_test_id("user-menu").click()
    logout_button = page.get_by_test_id("logout-button")
    expect(logout_button).to_have_text(
        build_ui_label_regex("layout.nav_bar.logout_button")
    )
    logout_button.click()
    expect(page.get_by_test_id("login-button")).to_be_visible()


@pytest.mark.parametrize(
    ("locale_id", "expected_nav_item_labels"),
    [
        pytest.param("de", ["Hochladen", "Durchsuchen"], id="locale de"),
        pytest.param("en", ["Upload", "Browse"], id="locale en"),
    ],
)
@pytest.mark.integration
def test_language_switcher_translates_nav_bar(
    page: Page,
    get_test_key: Callable[[str], str],
    base_url: str,
    locale_id: str,
    expected_nav_item_labels: list[str],
) -> None:
    expected_login_button_label = LocaleService.get().get_ui_label(
        locale_id, "login.button_login"
    )
    page.goto(base_url)
    page.get_by_test_id("input-x-system").fill("test")
    page.get_by_test_id("input-api-key").fill(get_test_key("test"))
    page.get_by_test_id("login-button").click()
    expect(page.get_by_test_id("nav-bar")).to_be_visible()

    # change language and wait for the new locale to be applied
    locale_segment = page.get_by_test_id(f"language-switcher-{locale_id}")
    locale_segment.click()
    expect(locale_segment).to_have_attribute("aria-pressed", "true")

    expect(page.get_by_test_id("nav-item-/")).to_have_text(expected_nav_item_labels[0])
    expect(page.get_by_test_id("nav-item-/browse")).to_have_text(
        expected_nav_item_labels[1]
    )
    page.screenshot(
        path=f"tests_test_login_test_language_switcher_nav_bar-{locale_id}.png",
    )

    # the login page has no switcher, so the locale is asserted via the login
    # button, which is already rendered in the locale picked before the logout
    page.get_by_test_id("user-menu").click()
    page.get_by_test_id("logout-button").click()
    expect(page.get_by_test_id("login-button")).to_have_text(
        expected_login_button_label
    )

    # logging back in keeps that locale, so `logout` restored it across `reset`
    page.get_by_test_id("input-x-system").fill("test")
    page.get_by_test_id("input-api-key").fill(get_test_key("test"))
    page.get_by_test_id("login-button").click()
    expect(page.get_by_test_id(f"language-switcher-{locale_id}")).to_have_attribute(
        "aria-pressed", "true"
    )
    expect(page.get_by_test_id("nav-item-/")).to_have_text(expected_nav_item_labels[0])


@pytest.mark.integration
def test_login_without_api_key_shows_translated_error(
    page: Page,
    base_url: str,
) -> None:
    page.goto(base_url)
    page.get_by_test_id("input-x-system").fill("test")

    page.get_by_test_id("login-button").click()

    expect(
        page.get_by_text(build_ui_label_regex("login.missing_api_key"))
    ).to_be_visible()
    page.screenshot(path="tests_test_login_test_login_without_api_key.png")


@pytest.mark.integration
def test_login_with_unknown_api_key_shows_translated_error(
    page: Page,
    base_url: str,
) -> None:
    page.goto(base_url)
    page.get_by_test_id("input-x-system").fill("test")
    page.get_by_test_id("input-api-key").fill("not-a-known-key")

    page.get_by_test_id("login-button").click()

    expect(
        page.get_by_text(build_ui_label_regex("login.unknown_api_key"))
    ).to_be_visible()
    page.screenshot(path="tests_test_login_test_login_with_unknown_api_key.png")
