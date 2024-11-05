import reflex as rx

from mex.drop.login.state import LoginState
from mex.drop.upload.main import mex_drop_logo


def login_form() -> rx.Component:
    """Return login form components."""
    return rx.card(
        rx.vstack(
            rx.vstack(
                rx.hstack(
                    rx.text(
                        "X System",
                        size="3",
                        weight="medium",
                    ),
                    justify="between",
                    width="100%",
                ),
                rx.input(
                    placeholder="Enter X System name",
                    on_change=LoginState.set_x_system,
                    type="text",
                    size="3",
                    width="100%",
                ),
                spacing="2",
                width="100%",
            ),
            rx.vstack(
                rx.text(
                    "API Key",
                    size="3",
                    weight="medium",
                    text_align="left",
                    width="100%",
                ),
                rx.input(
                    placeholder="Enter API key",
                    on_change=LoginState.set_api_key,
                    type="password",
                    size="3",
                    width="100%",
                ),
                justify="start",
                spacing="2",
                width="100%",
            ),
            rx.button("Log in", on_change=LoginState.login, size="3", width="100%"),
            spacing="6",
            width="100%",
        ),
        size="4",
        max_width="28em",
        width="100%",
    )


def index() -> rx.Component:
    """Return the index for the login component."""
    return rx.center(
        rx.card(
            rx.vstack(
                mex_drop_logo(),
                rx.divider(size="4"),
                login_form(),
                spacing="4",
            ),
            top="20vh",
            width="400px",
            variant="classic",
            custom_attrs={"data-testid": "login-card"},
        ),
    )
