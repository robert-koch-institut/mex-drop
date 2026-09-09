import reflex as rx
from fastapi import HTTPException
from reflex.event import EventSpec

from mex.drop.label_var import label_var
from mex.drop.models import User
from mex.drop.security import get_current_authorized_x_systems, is_authorized
from mex.drop.state import State


class LoginState(State):
    """State management for the login page."""

    api_key: str
    x_system: str

    @label_var(label_id="login.x_system")
    def label_x_system(self) -> None:
        """Label for x_system."""

    @label_var(label_id="login.api_key")
    def label_api_key(self) -> None:
        """Label for api_key."""

    @label_var(label_id="login.button_login")
    def label_button_login(self) -> None:
        """Label for button_login."""

    @label_var(label_id="login.invalid_credentials")
    def label_invalid_credentials(self) -> None:
        """Label for invalid_credentials."""

    @label_var(label_id="login.missing_api_key")
    def label_missing_api_key(self) -> None:
        """Label for missing_api_key."""

    @label_var(label_id="login.unknown_api_key")
    def label_unknown_api_key(self) -> None:
        """Label for unknown_api_key."""

    @rx.event
    def set_api_key(self, api_key: str) -> None:
        """Set the api_key."""
        self.api_key = api_key

    @rx.event
    def set_x_system(self, x_system: str) -> None:
        """Set the x_system."""
        self.x_system = x_system

    @rx.event
    def login(self) -> EventSpec:
        """Login the user."""
        if not self.api_key:
            return rx.toast.error(self.label_missing_api_key)
        try:
            authorized_x_systems = get_current_authorized_x_systems(
                api_key=self.api_key
            )
        except HTTPException:
            return rx.toast.error(self.label_unknown_api_key)
        if is_authorized(str(self.x_system), authorized_x_systems):
            self.user = User(
                api_key=self.api_key,
                x_system=self.x_system,
            )
            # reset api_key/x_system
            self.reset()  # type: ignore[no-untyped-call]
            return rx.redirect("/")
        return rx.toast.error(self.label_invalid_credentials)
