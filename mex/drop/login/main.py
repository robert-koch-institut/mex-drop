import reflex as rx

from mex.drop.layout import app_logo
from mex.drop.login.state import LoginState


def login_x_system() -> rx.Component:
    """Return a form field for the X-System."""
    return rx.vstack(
        rx.text("X-System"),
        rx.input(
            autofocus=True,
            name="x_system",
            on_change=LoginState.set_x_system,
            placeholder="X-System",
            size="3",
            tab_index=1,
            style={"width": "100%"},
        ),
        style={"width": "100%"},
    )


def login_api_key() -> rx.Component:
    """Return a form field for the API key."""
    return rx.vstack(
        rx.text("API Key"),
        rx.input(
            on_change=LoginState.set_api_key,
            name="api_key",
            placeholder="API Key",
            size="3",
            tab_index=2,
            type="password",
            style={"width": "100%"},
        ),
        style={"width": "100%"},
    )


def login_button() -> rx.Component:
    """Return a submit button for the login form."""
    return rx.hstack(
        rx.spacer(),
        rx.button(
            "Login",
            size="3",
            tab_index=3,
            style={
                "padding": "0 var(--space-6)",
                "marginTop": "var(--space-4)",
            },
            custom_attrs={"data-testid": "login-button"},
            type="submit",
        ),
        style={"width": "100%"},
    )


def index() -> rx.Component:
    """Return the index for the login component."""
    return rx.center(
        rx.card(
            rx.vstack(
                rx.hstack(
                    app_logo(),
                    rx.spacer(spacing="4"),
                    rx.color_mode.button(),
                    style={"width": "100%"},
                ),
                rx.divider(size="4"),
                rx.form(
                    rx.vstack(
                        login_x_system(),
                        login_api_key(),
                        login_button(),
                        style={"width": "100%"},
                    ),
                    on_submit=LoginState.login,
                    spacing="4",
                ),
            ),
            style={
                "width": "calc(340px * var(--scaling))",
                "padding": "var(--space-4)",
                "top": "20vh",
            },
            custom_attrs={"data-testid": "login-card"},
        )
    )
