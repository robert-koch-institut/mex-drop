import reflex as rx
from reflex.event import EventSpec

from mex.drop.label_var import label_var
from mex.drop.locale_service import LocaleService
from mex.drop.models import NavItem, User


class State(rx.State):
    """The app state."""

    _locale_service = LocaleService.get()
    _available_locales = _locale_service.get_available_locales()

    current_locale: str = next(
        (x for x in _available_locales if x.id.lower().startswith("de")),
        _available_locales[0],
    ).id
    user: User | None = None

    _nav_items: list[NavItem] = [
        NavItem(
            title="layout.nav_bar.upload_navitem",
            route_ids=["/", "/index"],
            raw_path="/",
        ),
        NavItem(
            title="layout.nav_bar.browse_navitem",
            route_ids=["/browse"],
            raw_path="/browse",
        ),
    ]

    def _translate_nav_item(self, item: NavItem) -> NavItem:
        return NavItem(
            title=self._locale_service.get_ui_label(self.current_locale, item.title),
            **item.model_dump(exclude={"title"}),
        )

    @rx.var(deps=["current_locale", "_nav_items"])
    def nav_items_translated(self) -> list[NavItem]:
        """The nav bar items with a locale sensitive label."""
        return [self._translate_nav_item(item) for item in self._nav_items]

    @label_var(label_id="layout.nav_bar.logout_button")
    def label_nav_bar_logout_button(self) -> None:
        """Label for nav_bar.logout_button."""

    @rx.event
    def change_locale(self, locale: str) -> None:
        """Change the current locale to the given one.

        Args:
            locale: The locale to change to.
        """
        self.current_locale = locale

    @rx.event
    def logout(self) -> EventSpec:
        """Log out the user, keeping the locale they picked."""
        current_locale = self.current_locale
        self.reset()  # type: ignore[no-untyped-call]
        self.current_locale = current_locale
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
        for nav_item in self._nav_items:
            nav_item.active = self.router.route_id in nav_item.route_ids
