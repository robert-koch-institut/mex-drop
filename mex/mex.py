import reflex as rx
from reflex.components.radix import themes
from reflex.utils.console import info as log_info

from mex.common.logging import logger
from mex.drop.api.main import check_system_status, router
from mex.drop.exceptions import custom_backend_handler
from mex.drop.file_history.main import index as file_history_index
from mex.drop.file_history.state import ListState
from mex.drop.login.main import index as login_index
from mex.drop.settings import DropSettings
from mex.drop.state import State
from mex.drop.upload.main import index as upload_index

app = rx.App(
    html_lang="en",
    theme=themes.theme(accent_color="blue", has_background=False),
    style={">a": {"opacity": "0"}},
)
app.add_page(
    upload_index,
    route="/",
    title="MEx Drop | Upload",
    on_load=[State.check_login, State.load_nav],
)
app.add_page(
    file_history_index,
    route="/file-history",
    title="MEx Drop | File History",
    on_load=[State.check_login, State.load_nav, ListState.refresh],
)
app.add_page(
    login_index,
    route="/login",
    title="MEx Drop | Login",
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
app.backend_exception_handler = custom_backend_handler

app.register_lifespan_task(
    lambda: logger.info(DropSettings.get().text()),
)
app.register_lifespan_task(
    log_info,
    msg="MEx Drop is running, shut it down using CTRL+C",
)
