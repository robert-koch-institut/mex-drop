import pathlib

from fastapi import (
    HTTPException,
    UploadFile,
)
from starlette import status

from mex.common.exceptions import MExError

ALLOWED_CONTENT_TYPES = {
    "application/json": ".json",
    "application/xml": ".xml",
    "application/vnd.ms-excel": ".xls",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
    "text/csv": ".csv",
    "text/xml": ".xml",
    "text/tab-separated-values": ".tsv",
}


def check_duplicate_filenames(files: list[UploadFile]) -> None:
    """Check for duplicate filenames."""
    if len(files) != len({file.filename for file in files}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Duplicate filename.",
        )
    return


async def write_to_file(content: bytes, out_file: pathlib.Path) -> None:
    """Write content to file. Parse content according to file type."""
    out_file.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(out_file, "wb") as f:
            f.write(content)
    except Exception as exc:
        raise MExError(
            f"Failed to write to file {out_file}: {exc!s}",
        ) from exc


async def validate_file_extension(content_type: str | None, filename: str) -> None:
    """Validate uploaded file content type and extension."""
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Unsupported content type: {content_type}. "
                f"Allowed types: {', '.join(ALLOWED_CONTENT_TYPES.values())}"
            ),
        )

    suffix = pathlib.Path(filename).suffix
    if suffix == ".csv" and content_type not in (
        "application/vnd.ms-excel",
        "text/csv",
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Content type doesn't match extension: "
            f"{content_type} != {filename}",
        )
    return
