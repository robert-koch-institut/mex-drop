from pydantic import Field, field_validator

from mex.common.settings import BaseSettings
from mex.common.types import WorkPath
from mex.drop.types import APIKey, UserDatabase, XSystem


class DropSettings(BaseSettings):
    """Settings definition for the drop server."""

    drop_api_host: str = Field(
        "localhost",
        min_length=1,
        max_length=250,
        description="Host that the drop api will run on.",
        validation_alias="MEX_DROP_API_HOST",
    )
    drop_api_port: int = Field(
        8021,
        gt=0,
        lt=65536,
        description="Port that the drop api should listen on.",
        validation_alias="MEX_DROP_API_PORT",
    )
    drop_frontend_port: int = Field(
        8020,
        gt=0,
        lt=65536,
        description="Port that the drop frontend should serve on.",
        validation_alias="MEX_DROP_FRONTEND_PORT",
    )
    drop_api_root_path: str = Field(
        "",
        description="Root path that the drop server should run under.",
        validation_alias="MEX_DROP_API_ROOT_PATH",
    )
    drop_directory: WorkPath = Field(
        WorkPath("data"),
        description="Root directory that the drop server should save files in, "
        "absolute or relative to `work_dir`.",
        validation_alias="MEX_DROP_DIRECTORY",
    )
    drop_api_key_database: UserDatabase = Field(
        UserDatabase({}),
        description="Database of API keys.",
        validation_alias="MEX_DROP_API_KEY_DATABASE",
    )

    @field_validator("drop_api_key_database", mode="before")
    @classmethod
    def validate_user_database(cls, value: dict[str, list[str]]) -> UserDatabase:
        """Ensure keys are APIKeys and values are XSystems."""
        return UserDatabase(
            {
                key if isinstance(key, APIKey) else APIKey(key): [
                    XSystem(x) for x in x_systems
                ]
                for key, x_systems in value.items()
            }
        )
