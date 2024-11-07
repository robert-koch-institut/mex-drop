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
    return rx.box(
        rx.hstack(
            mex_drop_logo(),
            rx.divider(orientation="vertical", size="2"),
            rx.hstack(
                navbar_link("Upload", "/upload"),
                navbar_link("File List", "/file-history"),
                justify="end",
                spacing="5",
            ),
            rx.button(
                "Logout",
                on_click=State.logout,
                size="3",
                bg="royalblue",
            ),
            justify="between",
            align_items="center",
        ),
        padding="2em",
        width="100%",
    )
