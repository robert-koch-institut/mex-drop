import reflex as rx
from reflex.event import EventSpec


def custom_backend_handler(exception: Exception) -> EventSpec:
    """Custom backend exception handler.

    Reflex calls this without a state, so there is no session locale to translate
    with. Errors that a user can actually act on are caught and translated in the
    state event that raises them, leaving only unexpected errors for this fallback.
    """
    return rx.toast.error(f"Backend Error: {exception}")
