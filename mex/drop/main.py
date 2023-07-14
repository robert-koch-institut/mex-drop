import re
from pathlib import Path
from typing import Annotated, Any

import uvicorn
from fastapi import APIRouter, Body, Depends, FastAPI, HTTPException
from pydantic import ConstrainedStr
from starlette import status

from mex.common.cli import entrypoint
from mex.drop.logging import UVICORN_LOGGING_CONFIG
from mex.drop.security import get_current_authorized_x_systems
from mex.drop.settings import DropSettings
from mex.drop.sinks.json import json_sink


class SafePath(ConstrainedStr):
    """String with restricted set of allowed characters.

    Allowed characters: a-z, A-Z, 0-9, -, _
    """

    regex = re.compile(r"^[a-zA-Z0-9_-]{1,128}$")


router = APIRouter(
    prefix="/v0",
)


@router.post("/{x_system}/{entity_type}", status_code=202)
async def post_data(
    x_system: SafePath,
    entity_type: SafePath,
    data: Annotated[
        dict[str, Any],
        Body(
            examples=[{"foo": "bar", "list": [1, 2, "foo"], "nested": {"foo": "bar"}}],
        ),
    ],
    x_systems: Annotated[list[str], Depends(get_current_authorized_x_systems)],
) -> None:
    """Upload arbitrary json data.

    Args:
        x_system: name of the x-system that the data comes from
        entity_type: name of the data file that is uploaded, if unsure use 'default'
        data: dictionary with string key and arbitrary values
        x_systems: list of authorized x-systems

    Settings:
        drop_root_path: where accepted data is stored
    """
    if x_system not in x_systems:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key not authorized for the current x_system",
            headers={"X-API-Key": ""},
        )
    settings = DropSettings.get()
    out_file = Path(settings.drop_root_path, x_system, entity_type + ".json")
    json_sink(data, out_file)


app = FastAPI(
    title="mex-drop",
    version="v0",
    contact={"name": "MEx Team", "email": "mex@rki.de"},
    description="Upload your data for the MEx service.",
)
app.include_router(router)


@entrypoint(DropSettings)
def main() -> None:  # pragma: no cover
    """Start the drop server process."""
    settings = DropSettings.get()
    uvicorn.run(
        "mex.drop.main:app",
        host=settings.drop_host,
        port=settings.drop_port,
        reload=settings.debug,
        log_config=UVICORN_LOGGING_CONFIG,
        headers=[("server", "mex-drop")],
    )
