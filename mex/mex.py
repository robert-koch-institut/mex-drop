import reflex as rx
from reflex.components.radix import themes

from mex.drop.api import check_system_status, router
from mex.drop.file_list.main import file_history_index
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
    route="/",
    title="MEx Drop",
    on_load=State.check_login,
)
app.add_page(
    login_index,
    route="/login",
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
