from uvicorn.config import LOGGING_CONFIG as DEFAULT_UVICORN_LOGGING_CONFIG

from mex.common.logging import logger

UVICORN_LOGGING_CONFIG = DEFAULT_UVICORN_LOGGING_CONFIG.copy()
UVICORN_LOGGING_CONFIG["loggers"][logger.name] = {
    "handlers": ["default"],
    "level": "INFO",
    "propagate": False,
}
