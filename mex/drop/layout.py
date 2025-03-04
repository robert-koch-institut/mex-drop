from typing import cast

import reflex as rx

from mex.drop.models import NavItem, User
from mex.drop.state import State


def user_button() -> rx.Component:
    """Return a user button with an icon that indicates their access rights."""
    return rx.button(
        rx.icon(tag="user_round_cog"),
        variant="ghost",
        style=rx.Style({"marginTop": "0"}),
    )


def user_menu() -> rx.Component:
    """Return a user menu with a trigger, the current X-System and a logout button."""
    return rx.menu.root(
        rx.menu.trigger(
            user_button(),
            custom_attrs={"data-testid": "user-menu"},
        ),
        rx.menu.content(
            rx.menu.item(cast(User, State.user).x_system, disabled=True),
            rx.menu.separator(),
            rx.menu.item(
                "Logout",
                on_select=State.logout,
            ),
        ),
    )


def nav_link(item: NavItem) -> rx.Component:
    """Return a link component for the given navigation item."""
    return rx.link(
        rx.text(item.title, size="4", weight="medium"),
        href=item.path,
        underline=item.underline,
        class_name="nav-item",
    )


def app_logo() -> rx.Component:
    """Return the app logo with icon and label."""
    return rx.hstack(
        rx.icon(
            "droplets",
            size=28,
        ),
        rx.heading(
            "MEx Drop",
            weight="medium",
            style=rx.Style({"userSelect": "none"}),
        ),
        custom_attrs={"data-testid": "app-logo"},
    )


def nav_bar() -> rx.Component:
    """Return a navigation bar component."""
    return rx.vstack(
        rx.box(
            style=rx.Style(
                {
                    "height": "var(--space-6)",
                    "width": "100%",
                    "backdropFilter": " var(--backdrop-filter-panel)",
                    "backgroundColor": "var(--card-background-color)",
                }
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
                rx.divider(orientation="vertical", size="2"),
                user_menu(),
                rx.spacer(),
                rx.color_mode.button(),
                justify="between",
                align_items="center",
            ),
            size="2",
            custom_attrs={"data-testid": "nav-bar"},
            style=rx.Style(
                {
                    "width": "100%",
                    "marginTop": "calc(-1 * var(--base-card-border-width))",
                }
            ),
        ),
        spacing="0",
        style=rx.Style(
            {
                "maxWidth": "calc(1480px * var(--scaling))",
                "minWidth": "calc(800px * var(--scaling))",
                "position": "fixed",
                "top": "0",
                "width": "100%",
                "zIndex": "1000",
            }
        ),
    )


def page(*children: rx.Component) -> rx.Component:
    """Return a page fragment with navigation bar and given children."""
    return rx.cond(
        State.user,
        rx.center(
            nav_bar(),
            rx.hstack(
                *children,
                style=rx.Style(
                    {
                        "maxWidth": "calc(1480px * var(--scaling))",
                        "minWidth": "calc(800px * var(--scaling))",
                        "padding": (
                            "calc(var(--space-6) * 4) var(--space-6) var(--space-6)"
                        ),
                        "width": "100%",
                    }
                ),
                custom_attrs={"data-testid": "page-body"},
            ),
        ),
        rx.center(
            rx.spinner(size="3"),
            style=rx.Style({"marginTop": "40vh"}),
        ),
    )
