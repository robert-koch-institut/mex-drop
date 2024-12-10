from typing import cast

import reflex as rx

from mex.drop.state import State


def mex_drop_logo() -> rx.Component:
    """Return the mex-drop logo with icon and label."""
    return rx.hstack(
        rx.icon(
            "droplets",
            size=28,
        ),
        rx.heading(
            "MEx Drop",
            weight="medium",
            style={"user-select": "none"},
        ),
        custom_attrs={"data-testid": "drop-logo"},
    )


def navbar_link(text: str, url: str) -> rx.Component:
    """Return a navigation bar item link."""
    return rx.link(rx.text(text, size="4", weight="medium"), href=url)


def nav_bar() -> rx.Component:
    """Return the navigation bar with logo, page links and logout button."""
    return rx.card(
        rx.hstack(
            mex_drop_logo(),
            rx.divider(size="2", orientation="vertical"),
            rx.hstack(
                navbar_link("Upload", "/upload"),
                navbar_link("File History", "/file-history"),
                justify="start",
                spacing="5",
            ),
            rx.spacer(spacing="4"),
            rx.button(
                "Logout",
                on_click=cast(State, State).logout(),
                size="3",
                bg="royalblue",
            ),
            justify="between",
            align_items="center",
        ),
        size="2",
        width="100%",
    )
