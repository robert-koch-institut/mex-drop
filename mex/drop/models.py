from typing import Literal

import reflex as rx


class User(rx.Base):
    """Info on the currently logged-in user."""

    x_system: str
    api_key: str


class NavItem(rx.Base):
    """Model for one navigation bar item."""

    title: str = ""
    path: str = "/"
    underline: Literal["always", "none"] = "none"
