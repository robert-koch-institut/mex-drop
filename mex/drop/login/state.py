import reflex as rx
from reflex.event import EventSpec

from mex.drop.security import get_current_authorized_x_systems, is_authorized
from mex.drop.state import State, User


class LoginState(State):
    """State management for the login page."""

    api_key: str
    x_system: str

    def set_api_key(self, value: str) -> None:
        """Set the API key."""
        self.api_key = value
        return

    def set_x_system(self, value: str) -> None:
        """Set the x_system."""
        self.x_system = value
        return

    def login_user(self) -> EventSpec:
        """Log in the user."""
        authorized_x_systems = get_current_authorized_x_systems(api_key=self.api_key)
        if not is_authorized(str(self.x_system), authorized_x_systems):
            return rx.toast.error(
                "API Key not authorized to drop data for this x_system.",
                close_button=True,
            )
        self.user = User(api_key=self.api_key, x_system=self.x_system)
        return rx.redirect("/")
