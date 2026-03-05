import os
import sys
from pathlib import Path

import uvicorn
from reflex import constants
from reflex.config import environment, get_config
from reflex.constants import Env
from reflex.reflex import run
from reflex.utils.build import setup_frontend_prod
from reflex.utils.console import set_log_level
from reflex.utils.exec import get_app_module, run_frontend_prod
from reflex.utils.prerequisites import get_compiled_app

from mex.drop.logging import UVICORN_LOGGING_CONFIG
from mex.drop.settings import DropSettings


def drop_api() -> None:  # pragma: no cover
    """Start the drop api."""
    settings = DropSettings.get()

    # Set the log level.
    set_log_level(constants.LogLevel.INFO)

    # Set environment variables.
    environment.REFLEX_ENV_MODE.set(Env.PROD)
    environment.REFLEX_SKIP_COMPILE.set(True)
    environment.REFLEX_USE_GRANIAN.set(False)

    # Reload the config to make sure the env vars are persistent.
    get_config(reload=True)

    # Run the api.
    uvicorn.run(
        get_app_module(),
        host=settings.drop_api_host,
        port=settings.drop_api_port,
        root_path=settings.drop_api_root_path,
        log_config=UVICORN_LOGGING_CONFIG,
        headers=[("server", "mex-drop")],
    )


def drop_frontend() -> None:  # pragma: no cover
    """Start the drop frontend."""
    settings = DropSettings.get()

    # Set the log level.
    set_log_level(constants.LogLevel.INFO)

    # Configure the environment.
    environment.REFLEX_ENV_MODE.set(Env.PROD)
    environment.REFLEX_CHECK_LATEST_VERSION.set(False)

    # Get the app module.
    get_compiled_app()

    # Set up the frontend for prod mode.
    setup_frontend_prod(Path.cwd())

    # Run the frontend.
    run_frontend_prod(
        Path.cwd(),
        str(settings.drop_frontend_port),
        backend_present=False,
    )


def main() -> None:  # pragma: no cover
    """Start the drop api together with frontend."""
    # Set environment variables.
    environment.REFLEX_USE_GRANIAN.set(False)
    environment.REFLEX_HOT_RELOAD_EXCLUDE_PATHS.set([Path("tests")])

    if "win32" in sys.platform:
        # bun cache is not working correctly on windows
        # https://github.com/oven-sh/bun/issues/20886
        os.environ["BUN_OPTIONS"] = "--no-cache"

    # Run drop service.
    run.main()
