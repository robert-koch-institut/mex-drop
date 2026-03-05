import reflex as rx
from reflex.components.radix import themes

from mex.drop.api.main import api as drop_api
from mex.drop.file_history.main import index as file_history_index
from mex.drop.file_history.state import ListState
from mex.drop.login.main import index as login_index
from mex.drop.state import State
from mex.drop.upload.main import index as upload_index
from mex.drop.utils import load_settings

app = rx.App(
    html_lang="en",
    theme=themes.theme(accent_color="blue", has_background=False),
    style={
        ">a": {"opacity": "0"},
    },
    api_transformer=drop_api,
)
app.add_page(
    upload_index,
    route="/",
    title="MEx Drop | Upload",
    on_load=[
        State.check_login,
        State.load_nav,
    ],
)
app.add_page(
    file_history_index,
    route="/file-history",
    title="MEx Drop | File History",
    on_load=[
        State.check_login,
        State.load_nav,
        ListState.refresh,
    ],
)
app.add_page(
    login_index,
    route="/login",
    title="MEx Drop | Login",
)
app.register_lifespan_task(
    load_settings,
)
