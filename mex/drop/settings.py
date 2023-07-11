from pydantic import Field

from mex.common.settings import BaseSettings
from mex.drop.types.user_database import UserDatabase


class DropSettings(BaseSettings):
    """Settings definition for the drop server."""

    drop_host: str = Field(
        "localhost",
        min_length=1,
        max_length=250,
        description="Host that the drop server will run on.",
        env="MEX_DROP_HOST",
    )
    drop_port: int = Field(
        8080,
        gt=0,
        lt=65536,
        description="Port that the drop server should listen on.",
        env="MEX_DROP_PORT",
    )
    drop_root_path: str = Field(
        "data",
        description="Root path that the drop server should run under.",
        env="MEX_DROP_ROOT_PATH",
    )
    drop_user_database: UserDatabase = Field(
        {},
        description="Database of users.",
        env="MEX_DROP_USER_DATABASE",
    )
