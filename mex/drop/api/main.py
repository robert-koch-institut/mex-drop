import pathlib
from importlib.metadata import version
from typing import Annotated, Any

from aiofile import async_open
from fastapi import (
    Body,
    Depends,
    FastAPI,
    File,
    Header,
    HTTPException,
    Path,
    Response,
    UploadFile,
)
from fastapi.responses import PlainTextResponse
from starlette import status
from starlette.background import BackgroundTask, BackgroundTasks

from mex.common.models import VersionStatus
from mex.drop.files_io import (
    ALLOWED_CONTENT_TYPES,
    check_duplicate_filenames,
    validate_file_extension,
    write_to_file,
)
from mex.drop.security import get_current_authorized_x_systems, is_authorized
from mex.drop.settings import DropSettings
from mex.drop.sinks.json import json_sink
from mex.drop.types import PATH_REGEX, EntityType, XSystem

api = FastAPI(
    title="mex-drop",
    version="v0",
    contact={"name": "MEx Team", "email": "mex@rki.de"},
    description="Upload and download data for the MEx service.",
)


@api.post(
    "/v0/{x_system}/{entity_type}",
    description="Upload arbitrary structured data to MEx.",
    tags=["api"],
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
                "Name of the data file that is uploaded, if unsure use 'default'"
            ),
        ),
    ],
    data: Annotated[
        dict[str, Any] | list[Any] | bytes,
        Body(
            description=(
                "An arbitrary data structure, that can be further processed by MEx"
            ),
            examples=[
                {"foo": "bar", "list": [1, 2, "foo"], "nested": {"foo": "bar"}},
                [{"foo": "bar"}, {"bar": [1, 2, 3]}],
            ],
        ),
    ],
    content_type: Annotated[
        str,
        Header(
            description=(
                f"Content-Type of the uploaded data.\n Allowed content types:"
                f"\n{', '.join(ALLOWED_CONTENT_TYPES.keys())}"
            ),
        ),
    ],
    authorized_x_systems: Annotated[
        list[XSystem], Depends(get_current_authorized_x_systems)
    ],
) -> Response:
    """Upload arbitrary data to MEx.

    Args:
        x_system: name of the x-system that the data comes from
        entity_type: name of the data file that is uploaded, if unsure use 'default'
        data: data content of request body
        authorized_x_systems: list of authorized x-systems
        content_type: Content-Type of the uploaded data

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
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported Content-Type. "
            f"Allowed types: {', '.join(ALLOWED_CONTENT_TYPES.keys())}",
        )
    file_ext = ALLOWED_CONTENT_TYPES[content_type]
    settings = DropSettings.get()
    out_file = settings.drop_directory / x_system / f"{entity_type}{file_ext}"
    if content_type == "application/json" and isinstance(data, (dict | list)):
        return Response(
            status_code=200, background=BackgroundTask(json_sink, data, out_file)
        )
    if isinstance(data, bytes):
        return Response(
            status_code=200, background=BackgroundTask(write_to_file, data, out_file)
        )
    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        detail="Unsupported content type or format.",
    )


@api.post(
    "/v0/{x_system}",
    description="Upload multipart file to MEx.",
    tags=["api"],
    status_code=202,
)
async def drop_data_multipart(
    x_system: Annotated[
        XSystem,
        Path(
            default=...,
            pattern=PATH_REGEX,
            description="Name of the system that the data comes from.",
        ),
    ],
    files: Annotated[
        list[UploadFile],
        File(
            description=(
                f"Multipart file list, that can be further processed by MEx.\n "
                f"Allowed file types: {', '.join(ALLOWED_CONTENT_TYPES.values())}"
            )
        ),
    ],
    authorized_x_systems: Annotated[
        list[XSystem], Depends(get_current_authorized_x_systems)
    ],
    background_tasks: BackgroundTasks,
) -> Response:
    """Upload multipart data to MEx.

    Args:
        x_system: name of the x-system that the data comes from
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
    check_duplicate_filenames(files)
    for file in files:
        entity_type = str(file.filename)
        await validate_file_extension(file.content_type, entity_type)
        content = await file.read()
        out_file = pathlib.Path(settings.drop_directory, x_system, entity_type)
        background_tasks.add_task(write_to_file, content, out_file)
    return Response(status_code=202)


@api.get(
    "/v0/{x_system}/{entity_type}",
    description="Download data from MEx.",
    tags=["api"],
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
        entity_type: name of the data file to download
        authorized_x_systems: list of authorized x-systems

    Settings:
        drop_directory: where data is stored

    Returns:
        A response
    """
    if not is_authorized(x_system, authorized_x_systems):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API Key not authorized to download data for this x_system.",
        )
    settings = DropSettings.get()
    out_file = pathlib.Path(settings.drop_directory, x_system, entity_type)
    if not out_file.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The requested data was not found on this server.",
        )
    async with async_open(out_file) as f:
        return Response(content=await f.read())


@api.get(
    "/v0/",
    description="List x-systems with available data.",
    tags=["api"],
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
        A response
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


@api.get(
    "/v0/{x_system}",
    description="List downloadable entities of an x-system.",
    tags=["api"],
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
        A response
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
    unique_extensions = {
        f"*{extension}" for extension in ALLOWED_CONTENT_TYPES.values()
    }
    return {
        "entity-types": [
            f.relative_to(x_system_data_dir).as_posix()
            for extension in unique_extensions
            for f in x_system_data_dir.glob(extension)
            if f.is_file()
        ]
    }


@api.get(
    "/_system/check",
    tags=["system"],
)
def check_system_status() -> VersionStatus:
    """Check that the drop server is healthy and responsive."""
    return VersionStatus(status="ok", version=version("mex-drop"))


def get_subdirectory_stats(base_path: pathlib.Path) -> list[tuple[str, int, float]]:
    """Scans a base path and returns stats for each immediate subdirectory.

    Returns:
        A list of tuples: (subdir_name, file_count, last_modified_timestamp)
    """
    stats = []
    base_path.mkdir(parents=True, exist_ok=True)
    for subdir in base_path.iterdir():
        if not subdir.is_dir():
            continue  # Skip files in the base directory

        dir_name = subdir.name
        file_count = 0

        all_mtimes = [subdir.stat().st_mtime]

        for item in subdir.iterdir():
            if item.is_file():
                file_count += 1
                all_mtimes.append(item.stat().st_mtime)

        last_mtime = max(all_mtimes)
        stats.append((dir_name, file_count, last_mtime))

    return stats


@api.get(
    "/_system/metrics",
    response_class=PlainTextResponse,
    tags=["system"],
)
def get_prometheus_metrics() -> str:
    """Get file system metrics for the drop directory."""
    settings = DropSettings.get()
    base_path = pathlib.Path(settings.drop_directory)
    stats = get_subdirectory_stats(base_path)

    file_count_metric = "drop_directory_files_count"
    last_mod_metric = "drop_directory_last_modified_timestamp"

    file_count_lines: list[str] = []
    last_mod_lines: list[str] = []

    for dir_name, file_count, last_mtime in stats:
        label = f'directory="{dir_name}"'

        file_count_lines.append(f"{file_count_metric}{{{label}}} {file_count}")
        last_mod_lines.append(f"{last_mod_metric}{{{label}}} {last_mtime}")

    output_blocks: list[str] = []

    if file_count_lines:
        output_blocks.append(
            f"# TYPE {file_count_metric} gauge\n" + "\n".join(file_count_lines)
        )
    if last_mod_lines:
        output_blocks.append(
            f"# TYPE {last_mod_metric} gauge\n" + "\n".join(last_mod_lines)
        )

    if output_blocks:
        return "\n\n".join(output_blocks) + "\n"

    return ""
