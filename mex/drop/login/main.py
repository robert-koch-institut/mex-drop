import reflex as rx

from mex.drop.layout import app_logo
from mex.drop.login.state import LoginState


def login_x_system() -> rx.Component:
    """Return a form field for the X-System."""
    return rx.vstack(
        rx.text("X-System"),
        rx.input(
            autofocus=True,
            on_change=LoginState.set_x_system,
            placeholder="X-System",
            size="3",
            tab_index=1,
            style={"width": "80%"},
        ),
        style={"width": "100%"},
    )


def login_api_key() -> rx.Component:
    """Return a form field for the API key."""
    return rx.vstack(
        rx.text("API key"),
        rx.input(
            on_change=LoginState.set_api_key,
            placeholder="API key",
            size="3",
            tab_index=2,
            type="password",
            style={"width": "80%"},
        ),
        style={"width": "100%"},
    )


def login_button() -> rx.Component:
    """Return a submit button for the login form."""
    return rx.button(
        "Log in",
        on_click=LoginState.login,
        size="3",
        tab_index=3,
        style={
            "padding": "0 var(--space-6)",
            "marginTop": "var(--space-4)",
        },
    )


def index() -> rx.Component:
    """Return the index for the login component."""
    return rx.center(
        rx.card(
            rx.vstack(
                app_logo(),
                rx.divider(size="4"),
                rx.vstack(
                    login_x_system(),
                    login_api_key(),
                    login_button(),
                    style={"width": "100%"},
                ),
                spacing="4",
            ),
            style={
                "width": "calc(400px * var(--scaling))",
                "top": "20vh",
            },
            variant="classic",
            custom_attrs={"data-testid": "login-card"},
        ),
    )
