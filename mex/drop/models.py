from pydantic import BaseModel


class User(BaseModel):
    """Info on the currently logged-in user."""

    x_system: str
    api_key: str


class NavItem(BaseModel):
    """Model for one navigation bar item."""

    title: str = ""
    path: str = "/"
    underline: str = "none"
