from pydantic import Field, validator

from mex.common.settings import BaseSettings
from mex.common.types import WorkPath
from mex.drop.types import APIKey, UserDatabase, XSystem


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
        8081,
        gt=0,
        lt=65536,
        description="Port that the drop server should listen on.",
        env="MEX_DROP_PORT",
    )
    drop_root_path: WorkPath = Field(
        "data",
        description="Root path that the drop server should run under, "
        "absolute or relative to `work_dir`.",
        env="MEX_DROP_ROOT_PATH",
    )
    drop_user_database: UserDatabase = Field(
        {},
        description="Database of users.",
        env="MEX_DROP_USER_DATABASE",
    )

    @validator("drop_user_database", pre=True)
    def validate_user_database(cls, value: dict[str, list[str]]) -> UserDatabase:
        """Ensure keys are APIKeys and values are XSystems."""
        return UserDatabase(
            {
                key
                if isinstance(key, APIKey)
                else APIKey(key): [XSystem(x) for x in x_systems]
                for key, x_systems in value.items()
            }
        )
