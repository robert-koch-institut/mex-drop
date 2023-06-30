import json
import re
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from pydantic import ConstrainedStr

OUTPUT_DIRECTORY = "."


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
    x_system: SafePath, entity_type: SafePath, data: dict[str, Any]
) -> None:
    """Post arbitrary json.

    Args:
        x_system: name of the x-system that the data comes from
        entity_type: name of the data file that is uploaded, if unsure use 'default'
        data: dictionary with string key and arbitrary values

    Returns:
        None
    """
    out_file = Path(OUTPUT_DIRECTORY, x_system, entity_type + ".json")

    if out_file.is_file():
        out_file.rename(out_file.as_posix() + ".bk")
    else:
        out_file.parent.mkdir(exist_ok=True)
    print(out_file.absolute().as_posix())
    with open(out_file, "w") as handle:
        json.dump(data, handle, sort_keys=True)
