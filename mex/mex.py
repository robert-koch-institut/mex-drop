import reflex as rx
from reflex.components.radix import themes
from reflex.event import EventSpec

from mex.drop.api import check_system_status, router
from mex.drop.file_history.main import file_history_index
from mex.drop.login.main import login_index
from mex.drop.settings import DropSettings
from mex.drop.state import State
from mex.drop.upload.main import upload_index

app = rx.App(
    html_lang="en",
    theme=themes.theme(accent_color="blue"),
)
app.add_page(
    upload_index,
    route="/upload",
    title="MEx Drop",
    on_load=State.check_login,  # type: ignore  # noqa: PGH003
)
app.add_page(
    login_index,
    route="/",
    title="MEx Drop | Login",
)
app.add_page(
    file_history_index,
    route="/file-history",
    title="MEx Drop | File History",
)
app.api.add_api_route(
    "/_system/check",
    check_system_status,
    tags=["system"],
)
app.api.title = "mex-drop"
app.api.version = "v0"
app.api.contact = {"name": "MEx Team", "email": "mex@rki.de"}
app.api.description = "Upload and download data for the MEx service."
app.api.include_router(router)
app.register_lifespan_task(
    DropSettings.get,
)


def custom_backend_handler(
    exception: Exception,
) -> EventSpec:
    """Custom backend exception handler."""
    if str(exception) == "401: Missing authentication header X-API-Key.":
        return rx.toast.error("Please enter your API key.")
    if str(exception) == "401: The provided API Key is not recognized.":
        return rx.toast.error("Invalid API key.")
    return rx.toast.error("Backend Error: " + str(exception))


app.backend_exception_handler = custom_backend_handler
