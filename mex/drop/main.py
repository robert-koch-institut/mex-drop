import typer
import uvicorn
from fastapi import (
    FastAPI,
)
from pydantic import BaseModel
from reflex.reflex import run
from uvicorn.config import LOGGING_CONFIG as DEFAULT_UVICORN_LOGGING_CONFIG

from mex.common.cli import entrypoint
from mex.common.logging import logger
from mex.drop.api import router
from mex.drop.settings import DropSettings

UVICORN_LOGGING_CONFIG = DEFAULT_UVICORN_LOGGING_CONFIG.copy()
UVICORN_LOGGING_CONFIG["loggers"][logger.name] = {
    "handlers": ["default"],
    "level": "INFO",
    "propagate": False,
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
def backend() -> None:  # pragma: no cover
    """Start the drop fastAPI backend."""
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


def main() -> None:  # pragma: no cover
    """Start the editor service."""
    typer.run(run)
