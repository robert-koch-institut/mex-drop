import reflex as rx


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


def index() -> rx.Component:
    """Return the index for the drop app."""
    return rx.center(
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
    )
