import reflex as rx
from reflex.event import EventSpec


def custom_backend_handler(exception: Exception) -> EventSpec:
    """Custom backend exception handler."""
    if str(exception) == "401: Missing authentication header X-API-Key.":
        return rx.toast.error("Please enter your API Key.")
    if str(exception) == "401: The provided API Key is not recognized.":
        return rx.toast.error("Invalid API Key.")
    return rx.toast.error(f"Backend Error: {exception}")
