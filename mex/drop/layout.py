from typing import cast

import reflex as rx

from mex.drop.locale_service import LocaleService, MExLocale
from mex.drop.models import NavItem, User
from mex.drop.state import State

locale_service = LocaleService.get()


def user_button() -> rx.Component:
    """Return a user button with an icon that indicates their access rights."""
    return rx.button(
        rx.icon("user_round_cog"),
        variant="ghost",
        style=rx.Style(marginTop="0"),
    )


def user_menu() -> rx.Component:
    """Return a user menu with a trigger, the current X-System and a logout button."""
    return rx.menu.root(
        rx.menu.trigger(
            user_button(),
            custom_attrs={"data-testid": "user-menu"},
        ),
        rx.menu.content(
            rx.menu.item(cast("User", State.user).x_system, disabled=True),
            rx.menu.separator(),
            rx.menu.item(
                State.label_nav_bar_logout_button,
                on_select=State.logout,
                custom_attrs={"data-testid": "logout-button"},
            ),
            align="end",
        ),
    )


def language_switcher_segment(locale: MExLocale) -> rx.Component:
    """Return one segment of the language switcher for the given locale."""
    is_current = State.current_locale == locale.id
    return rx.button(
        locale.code,
        on_click=State.change_locale(locale.id),  # type: ignore[operator]
        title=locale.label,
        variant="ghost",
        radius="none",
        style=rx.Style(
            margin="0",
            paddingLeft="var(--space-3)",
            paddingRight="var(--space-3)",
            fontWeight="var(--font-weight-bold)",
            backgroundColor=rx.cond(is_current, "var(--accent-11)", "transparent"),
            # gray-1 inverts with the color mode, staying readable on the accent fill
            color=rx.cond(is_current, "var(--gray-1)", "var(--accent-11)"),
        ),
        _hover={
            "backgroundColor": rx.cond(
                is_current, "var(--accent-11)", rx.color("accent", 4)
            ),
        },
        custom_attrs={
            "data-testid": f"language-switcher-{locale.id}",
            "aria-pressed": is_current,
        },
    )


def language_switcher() -> rx.Component:
    """Return a language switcher with one button segment per available locale."""
    return rx.hstack(
        rx.foreach(
            locale_service.get_available_locales(),
            language_switcher_segment,
        ),
        spacing="0",
        style=rx.Style(
            alignItems="stretch",
            border=f"1px solid {rx.color('accent', 8)}",
            borderRadius="var(--radius-3)",
            overflow="hidden",
        ),
        custom_attrs={"data-testid": "language-switcher"},
    )


def nav_link(item: NavItem) -> rx.Component:
    """Return a link component for the given navigation item."""
    return rx.link(
        rx.text(item.title, size="4", weight="medium"),
        href=item.raw_path,
        underline=rx.cond(item.active, "always", "none"),
        class_name=rx.cond(item.active, "nav-item nav-item-active", "nav-item"),
        custom_attrs={"data-testid": f"nav-item-{item.route_ids[0]}"},
    )


def app_logo() -> rx.Component:
    """Return the app logo with icon and label."""
    return rx.hstack(
        rx.icon("droplets", size=28),
        rx.heading(
            "MEx Drop",
            weight="medium",
            style=rx.Style(userSelect="none"),
        ),
        custom_attrs={"data-testid": "app-logo"},
    )


def nav_bar() -> rx.Component:
    """Return a navigation bar component."""
    return rx.vstack(
        rx.box(
            style=rx.Style(
                height="var(--space-6)",
                width="100%",
                backdropFilter="var(--backdrop-filter-panel)",
            ),
        ),
        rx.card(
            rx.hstack(
                app_logo(),
                rx.divider(orientation="vertical", size="2"),
                rx.hstack(
                    rx.foreach(State.nav_items_translated, nav_link),
                    justify="start",
                    spacing="4",
                ),
                rx.spacer(),
                rx.hstack(
                    language_switcher(),
                    user_menu(),
                    align="center",
                    spacing="4",
                ),
                justify="between",
                align_items="center",
            ),
            size="2",
            custom_attrs={"data-testid": "nav-bar"},
            style=rx.Style(
                width="100%",
                marginTop="calc(-1 * var(--base-card-border-width))",
            ),
        ),
        spacing="0",
        style=rx.Style(
            maxWidth="var(--app-max-width)",
            minWidth="var(--app-min-width)",
            position="fixed",
            top="0",
            width="100%",
            zIndex="1000",
        ),
    )


def page(*children: rx.Component) -> rx.Component:
    """Return a page fragment with navigation bar and given children."""
    page_content = [
        nav_bar(),
        rx.hstack(
            *children,
            style=rx.Style(
                maxWidth="var(--app-max-width)",
                minWidth="var(--app-min-width)",
                padding="calc(var(--space-6) * 4) var(--space-6) var(--space-6)",
                width="100%",
            ),
            custom_attrs={"data-testid": "page-body"},
        ),
    ]

    return rx.cond(
        State.user,
        rx.center(
            *page_content,
            style=rx.Style(
                {
                    "--app-max-width": "calc(1480px * var(--scaling))",
                    "--app-min-width": "calc(800px * var(--scaling))",
                    "width": "100%",
                }
            ),
        ),
        rx.center(
            rx.spinner(size="3"),
            style=rx.Style(marginTop="40vh"),
        ),
    )
