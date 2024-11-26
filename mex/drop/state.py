import reflex as rx
from reflex.event import EventSpec


class User(rx.Base):
    """Info on the currently logged-in user."""

    x_system: str
    api_key: str


class State(rx.State):
    """The app state."""

    user: User | None = None

    def logout(self) -> EventSpec:
        """Log out the user."""
        self.reset()
        return rx.redirect("/")

    def check_login(self) -> EventSpec | None:
        """Check if the user is logged in."""
        if self.user is None:
            return rx.redirect("/")
        return None
