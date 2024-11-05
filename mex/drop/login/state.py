import reflex as rx
from reflex.event import EventSpec

from mex.drop.security import get_current_authorized_x_systems, is_authorized
from mex.drop.state import State, User


class LoginState(State):
    """State management for the login page."""

    api_key: str
    x_system: str

    def login(self) -> EventSpec:
        """Log in the user."""
        authorized_x_systems = get_current_authorized_x_systems(api_key=self.api_token)
        if not is_authorized(str(self.x_system), authorized_x_systems):
            return rx.toast.error(
                "API Key not authorized to drop data for this x_system.",
                close_button=True,
            )
        self.user = User(api_token=self.api_key, x_system=self.x_system)
        return rx.redirect("/")
