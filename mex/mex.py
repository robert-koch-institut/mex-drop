import reflex as rx
from reflex.components.radix import themes

from mex.drop.api.main import api as drop_api
from mex.drop.browse.main import index as browse_index
from mex.drop.browse.state import BrowseState
from mex.drop.exceptions import custom_backend_handler
from mex.drop.login.main import index as login_index
from mex.drop.state import State
from mex.drop.upload.main import index as upload_index
from mex.drop.utils import load_settings

app = rx.App(
    theme=themes.theme(
        accent_color="blue",
        has_background=False,
        appearance="light",
    ),
    style={
        ">a": {"opacity": "0"},
    },
    api_transformer=drop_api,
    backend_exception_handler=custom_backend_handler,
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
    browse_index,
    route="/browse",
    title="MEx Drop | Browse",
    on_load=[
        State.check_login,
        State.load_nav,
        BrowseState.refresh,
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
