import reflex as rx

from mex.drop.navigation import mex_drop_logo, nav_bar


def file_history_index() -> rx.Component:
    """Return the index for the file history page."""
    return rx.box(
        nav_bar(),
        rx.center(
            rx.card(
                rx.vstack(
                    mex_drop_logo(),
                    rx.divider(size="4"),
                    rx.text(
                        "This page is not yet implemented.",
                    ),
                    spacing="4",
                ),
                top="20vh",
                width="400px",
                variant="classic",
                custom_attrs={"data-testid": "index-card"},
            ),
        ),
        background_color="var(--gray-2)",
        min_height="100vh",
        padding="2em",
    )
