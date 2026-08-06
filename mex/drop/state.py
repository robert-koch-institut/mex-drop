import reflex as rx
from reflex.event import EventSpec

from mex.drop.models import NavItem, User


class State(rx.State):
    """The app state."""

    user: User | None = None
    nav_items: list[NavItem] = [
        NavItem(
            title="Upload",
            path="/",
        ),
        NavItem(
            title="File History",
            path="/file-history",
        ),
    ]

    @rx.event
    def logout(self) -> EventSpec:
        """Log out the user."""
        self.reset()
        return rx.redirect("/")

    @rx.event
    def check_login(self) -> EventSpec | None:
        """Check if the user is logged in."""
        if self.user is None:
            return rx.redirect("/login")
        return None

    @rx.event
    def load_nav(self) -> None:
        """Event hook for updating the navigation on page loads."""
        for nav_item in self.nav_items:
            if self.router.page.path == nav_item.path:
                nav_item.underline = "always"
            else:
                nav_item.underline = "none"
