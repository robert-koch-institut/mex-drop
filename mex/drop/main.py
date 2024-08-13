import io
import pathlib
from typing import Annotated, Any

import pandas as pd
import uvicorn
from fastapi import (
    APIRouter,
    Body,
    Depends,
    FastAPI,
    File,
    HTTPException,
    Path,
    Request,
    Response,
    UploadFile,
)
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from starlette import status
from starlette.background import BackgroundTask, BackgroundTasks

from mex.common.cli import entrypoint
from mex.common.exceptions import MExError
from mex.drop.logging import UVICORN_LOGGING_CONFIG
from mex.drop.security import get_current_authorized_x_systems, is_authorized
from mex.drop.settings import DropSettings
from mex.drop.sinks.json import json_sink
from mex.drop.types import PATH_REGEX, EntityType, XSystem

templates = Jinja2Templates(directory=pathlib.Path(__file__).parent / "templates")
router = APIRouter(
    prefix="/v0",
)

ALLOWED_FORMATS = {"json", "xml", "xls", "xlsx", "csv", "tsv"}
ALLOWED_CONTENT_TYPES = {
    "application/json": "json",
    "application/xml": "xml",
    "application/vnd.ms-excel": "xls",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
    "text/csv": "csv",
    "text/tab-separated-values": "tsv",
}


@router.post(
    "/{x_system}/{entity_type}",
    description="Upload arbitrary structured data to MEx.",
    tags=["API"],
    status_code=202,
)
async def drop_data(
    x_system: Annotated[
        XSystem,
        Path(
            default=...,
            pattern=PATH_REGEX,
            description="Name of the system that the data comes from",
        ),
    ],
    entity_type: Annotated[
        EntityType,
        Path(
            default=...,
            pattern=PATH_REGEX,
            description=(
                "Name of the data file that is uploaded, " "if unsure use 'default'"
            ),
        ),
    ],
    data: Annotated[
        dict[str, Any] | list[Any] | str | bytes,
        Body(
            description=(
                "An arbitrary data structure, " "that can be further processed by MEx"
            ),
            examples=[
                {"foo": "bar", "list": [1, 2, "foo"], "nested": {"foo": "bar"}},
                "foo,bar\n1,2",
                '{"foo": "bar"}',
                "<root><foo>bar</foo></root>",
            ],
            media_type="text/csv",
        ),
    ],
    authorized_x_systems: Annotated[
        list[XSystem], Depends(get_current_authorized_x_systems)
    ],
    request: Request,
) -> Response:
    """Upload arbitrary structured data to MEx.

    Args:
        x_system: name of the x-system that the data comes from
        entity_type: name of the data file that is uploaded, if unsure use 'default'
        data: dictionary with string keys or list with and arbitrary values
        authorized_x_systems: list of authorized x-systems
        request: HTTP Request class
        content: content of uploaded file

    Settings:
        drop_directory: where accepted data is stored

    Returns:
        A JSON response
    """
    if not is_authorized(x_system, authorized_x_systems):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API Key not authorized to drop data for this x_system.",
        )
    content_type = request.headers.get("Content-Type")
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported Content-Type. "
            f"Allowed types: {', '.join(ALLOWED_CONTENT_TYPES.keys())}",
        )
    file_ext = ALLOWED_CONTENT_TYPES[content_type]
    settings = DropSettings.get()
    out_file = pathlib.Path(
        settings.drop_directory, x_system + f"/{entity_type}.{file_ext}"
    )
    if content_type == "application/json":
        json_data = await request.json()
        return Response(
            status_code=202, background=BackgroundTask(json_sink, json_data, out_file)
        )
    raw_data = await request.body()
    return Response(
        status_code=200, background=BackgroundTask(write_to_file, raw_data, out_file)
    )


@router.post(
    "/{x_system}",
    description="Upload multipart file to MEx.",
    tags=["API"],
    status_code=202,
)
async def drop_data_mulitpoint(
    x_system: Annotated[
        XSystem,
        Path(
            default=...,
            pattern=PATH_REGEX,
            description="Name of the system that the data comes from",
        ),
    ],
    files: Annotated[
        list[UploadFile],
        File(
            description=("Multipart file list, " "that can be further processed by MEx")
        ),
    ],
    authorized_x_systems: Annotated[
        list[XSystem], Depends(get_current_authorized_x_systems)
    ],
    background_tasks: BackgroundTasks,
) -> Response:
    """Upload multipoint data to MEx.

    Args:
        x_system: name of the x-system that the data comes from
        entity_type: name of the data file that is uploaded, if unsure use 'default'
        files: list of files to be uploaded to MEx
        authorized_x_systems: list of authorized x-systems
        background_tasks: collection of background tasks

    Settings:
        drop_directory: where accepted data is stored

    Returns:
        A JSON response
    """
    if not is_authorized(x_system, authorized_x_systems):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API Key not authorized to drop data for this x_system.",
        )
    settings = DropSettings.get()
    for file in files:
        entity_type = str(file.filename)
        await validate_file_extension(entity_type)
    for file in files:
        content = await file.read()
        entity_type = str(file.filename)
        out_file = pathlib.Path(settings.drop_directory, x_system, entity_type)
        background_tasks.add_task(write_to_file, content, out_file)
    return Response(status_code=202)


async def write_to_file(
    content: bytes, out_file: pathlib.Path, content_type: str = ""
) -> None:
    """Write content to file. Parse content according to file type."""
    out_file.parent.mkdir(parents=True, exist_ok=True)
    try:
        if content_type == "text/csv" or content_type == "text/tab-separated-values":
            decoded_data = content.decode("utf-8")
            with open(out_file, "w", newline="") as f:
                f.write(decoded_data)
        elif content_type == "application/xml":
            decoded_data = content.decode("utf-8")
            with open(out_file, "w") as f:
                f.write(decoded_data)
        elif (
            content_type == "application/vnd.ms-excel"
            or content_type
            == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ):
            file_stream = io.BytesIO(content)
            df = pd.read_excel(file_stream, sheet_name=None)
            with pd.ExcelWriter(out_file, engine="openpyxl") as writer:
                for sheet_name, sheet_data in df.items():
                    sheet_data.to_excel(writer, sheet_name=sheet_name, index=False)
        with open(out_file, "wb") as f:
            f.write(content)
    except Exception as exc:
        raise MExError(
            f"Failed to write to file {out_file}: {exc!s}",
        ) from exc


async def validate_file_extension(filename: str) -> None:
    """Validate uploaded file format."""
    if "." in filename:
        extension = filename.rsplit(".", 1)[1].lower()
        if extension in ALLOWED_FORMATS:
            return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=f"Unsupported file extension: {filename}",
    )


@router.get(
    "/{x_system}/{entity_type}",
    description="Download data from MEx.",
    tags=["API"],
)
async def download_data(
    x_system: Annotated[
        XSystem,
        Path(
            default=...,
            pattern=PATH_REGEX,
            description="Name of the system that the data comes from",
        ),
    ],
    entity_type: Annotated[
        EntityType,
        Path(
            default=...,
            pattern=PATH_REGEX,
            description=("Name of the file that is uploaded, if unsure use 'default'"),
        ),
    ],
    authorized_x_systems: Annotated[
        list[XSystem], Depends(get_current_authorized_x_systems)
    ],
) -> Response:
    """Download data from MEx.

    Args:
        x_system: name of the x-system that is the original data source
        entity_type: name of the data file to download, without json extension
        authorized_x_systems: list of authorized x-systems

    Settings:
        drop_directory: where data is stored

    Returns:
        A JSON response
    """
    if not is_authorized(x_system, authorized_x_systems):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API Key not authorized to download data for this x_system.",
        )
    settings = DropSettings.get()
    out_file = pathlib.Path(settings.drop_directory, x_system, entity_type + ".json")
    if not out_file.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The requested data was not found on this server.",
        )
    with out_file.open() as handle:
        return Response(content=handle.read())


@router.get(
    "/",
    description="List x-systems with available data.",
    tags=["API"],
)
def list_x_systems(
    authorized_x_systems: Annotated[
        list[XSystem], Depends(get_current_authorized_x_systems)
    ],
) -> dict[str, list[str]]:
    """List x-systems with available data.

    Args:
        authorized_x_systems: list of authorized x-systems

    Settings:
        drop_directory: where data is stored

    Returns:
        A JSON response
    """
    if not is_authorized(XSystem("admin"), authorized_x_systems):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API Key not authorized to list x_systems.",
        )
    settings = DropSettings.get()
    return {
        "x-systems": [
            f.relative_to(settings.drop_directory).as_posix()
            for f in pathlib.Path(settings.drop_directory).glob("*")
            if f.is_dir()
        ]
    }


@router.get(
    "/{x_system}",
    description="List downloadable entities of an x-system.",
    tags=["API"],
)
def list_entity_types(
    x_system: Annotated[
        XSystem,
        Path(
            default=...,
            pattern=PATH_REGEX,
            description="Name of the system that the data comes from",
        ),
    ],
    authorized_x_systems: Annotated[
        list[XSystem], Depends(get_current_authorized_x_systems)
    ],
) -> dict[str, list[str]]:
    """List available files for an x-system.

    Args:
        x_system: name of the x-system that the data comes from
        authorized_x_systems: list of authorized x-systems

    Settings:
        drop_directory: where data is stored

    Returns:
        A JSON response
    """
    if not is_authorized(x_system, authorized_x_systems):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API Key not authorized to list files for this x_system.",
        )
    settings = DropSettings.get()
    x_system_data_dir = pathlib.Path(settings.drop_directory, x_system)
    if not x_system_data_dir.is_dir():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The requested x-system was not found on this server.",
        )
    return {
        "entity-types": [
            f.relative_to(x_system_data_dir).as_posix().removesuffix(".json")
            for f in x_system_data_dir.glob("*.json")
            if f.is_file()
        ]
    }


app = FastAPI(
    title="mex-drop",
    version="v0",
    contact={"name": "MEx Team", "email": "mex@rki.de"},
    description="Upload and download data for the MEx service.",
)
app.include_router(router)


class SystemStatus(BaseModel):
    """Response model for system status check."""

    status: str


@app.get("/_system/check", tags=["system"])
def check_system_status() -> SystemStatus:
    """Check that the drop server is healthy and responsive."""
    return SystemStatus(status="ok")


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
