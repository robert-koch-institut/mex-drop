import json
import re
from pathlib import Path
from typing import Annotated, Any

import uvicorn
from fastapi import Body, FastAPI
from pydantic import ConstrainedStr

from mex.common.cli import entrypoint
from mex.drop.logging import UVICORN_LOGGING_CONFIG
from mex.drop.settings import DropSettings


class SafePath(ConstrainedStr):
    """String with restricted set of allowed characters.

    Allowed characters: a-z, A-Z, 0-9, -, _
    """

    regex = re.compile(r"^[a-zA-Z0-9_-]+$")


app = FastAPI(title="mex-drop", version="v0")


@app.get("/")
def read_root() -> dict[str, str]:
    """Get hello world object from api root."""
    return {"Hello": "World"}


@app.post("/{x_system}/{entity_type}")
async def post_data(
    x_system: SafePath,
    entity_type: SafePath,
    data: Annotated[
        dict[str, Any],
        Body(
            example={"foo": "bar", "list": [1, 2, "foo"], "nested": {"foo": "bar"}},
        ),
    ],
) -> None:
    """Post arbitrary json.

    Args:
        x_system: name of the x-system that the data comes from
        entity_type: name of the data file that is uploaded, if unsure use 'default'
        data: dictionary with string key and arbitrary values

    Returns:
        None
    """
    settings = DropSettings.get()
    out_file = Path(settings.drop_root_path, x_system, entity_type + ".json")

    if out_file.is_file():
        out_file.rename(out_file.as_posix() + ".bk")
    else:
        out_file.parent.mkdir(exist_ok=True, parents=True)
    with open(out_file, "w") as handle:
        json.dump(data, handle, sort_keys=True)


@entrypoint(DropSettings)
def main() -> None:  # pragma: no cover
    """Start the drop server process."""
    settings = DropSettings.get()
    uvicorn.run(
        "mex.drop.main:app",
        host=settings.drop_host,
        port=settings.drop_port,
        root_path=settings.drop_root_path,
        reload=settings.debug,
        log_config=UVICORN_LOGGING_CONFIG,
        headers=[("server", "mex-drop")],
    )
