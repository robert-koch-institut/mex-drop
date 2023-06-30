import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI


OUTPUT_DIRECTORY = "."


app = FastAPI(
    title="mex-drop",
    version="v0"
)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/{x_system}/{entity_type}")
async def post_data(x_system: str, entity_type: str, data: dict[str, Any]) -> None:
    out_file = Path(OUTPUT_DIRECTORY, x_system, entity_type + ".json")

    if out_file.is_file():
        out_file.rename(out_file.as_posix() + ".bk")
    else:
        out_file.parent.mkdir(exist_ok=True)
    print(out_file.absolute().as_posix())
    with open(out_file, "w") as handle:
        json.dump(data, handle, sort_keys=True)
