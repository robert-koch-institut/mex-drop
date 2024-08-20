import reflex as rx
from reflex.components.radix import themes

from mex.drop.api import check_system_status, router
from mex.drop.main import index
from mex.drop.settings import DropSettings

app = rx.App(
    html_lang="en",
    theme=themes.theme(accent_color="blue"),
)
app.add_page(
    index,
    route="/",
    title="MEx Drop",
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
