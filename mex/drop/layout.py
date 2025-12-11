from typing import cast

import reflex as rx

from mex.drop.models import NavItem, User
from mex.drop.state import State


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
                "Logout",
                on_select=State.logout,
                custom_attrs={"data-testid": "logout-button"},
            ),
            align="end",
        ),
    )


def nav_link(item: NavItem) -> rx.Component:
    """Return a link component for the given navigation item."""
    return rx.link(
        rx.text(item.title, size="4", weight="medium"),
        href=item.path,
        underline=item.underline,  # type: ignore[arg-type]
        class_name="nav-item",
    )


def app_logo() -> rx.Component:
    """Return the app logo with icon and label."""
    return rx.hover_card.root(
        rx.hover_card.trigger(
            rx.hstack(
                rx.icon("droplets", size=28),
                rx.heading(
                    "MEx Drop",
                    weight="medium",
                    style=rx.Style(userSelect="none"),
                ),
                custom_attrs={"data-testid": "app-logo"},
            )
        ),
        rx.hover_card.content(
            rx.vstack(
                rx.code(f"mex-drop=={State.drop_version}", variant="outline"),
            ),
        ),
        open_delay=500,
    )


def nav_bar() -> rx.Component:
    """Return a navigation bar component."""
    return rx.vstack(
        rx.box(
            style=rx.Style(
                height="var(--space-6)",
                width="100%",
                backdropFilter="var(--backdrop-filter-panel)",
                backgroundColor="var(--card-background-color)",
            ),
        ),
        rx.card(
            rx.hstack(
                app_logo(),
                rx.divider(orientation="vertical", size="2"),
                rx.hstack(
                    rx.foreach(State.nav_items, nav_link),
                    justify="start",
                    spacing="4",
                ),
                rx.spacer(),
                rx.hstack(
                    user_menu(),
                    rx.button(
                        rx.icon("sun_moon"),
                        variant="ghost",
                        style=rx.Style(marginTop="0"),
                        on_click=rx.toggle_color_mode,
                    ),
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
                }
            ),
        ),
        rx.center(
            rx.spinner(size="3"),
            style=rx.Style(marginTop="40vh"),
        ),
    )
