import json
from pathlib import Path
from typing import Any

from mex.common.logging import logger


def json_sink(data: dict[str, Any] | list[Any], out_file: Path) -> None:
    """Write data as json to file.

    Args:
        data: dictionary or list that is dumped as json
        out_file: path to output file, parent directories are created if they do not
            exist

    Returns:
        None
    """
    out_file.parent.mkdir(exist_ok=True, parents=True)
    with out_file.open("w", encoding="utf-8") as handle:
        logger.info(f"writing data to {out_file.absolute().as_posix()}")
        json.dump(data, handle, sort_keys=True)
