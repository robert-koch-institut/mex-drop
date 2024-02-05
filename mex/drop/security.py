from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader
from starlette import status

from mex.drop.settings import DropSettings
from mex.drop.types import APIKey, UserDatabase, XSystem

X_API_KEY = APIKeyHeader(name="X-API-Key", auto_error=False)


def get_authorized_x_systems(
    user_database: UserDatabase, api_key: APIKey
) -> list[XSystem] | None:
    """Get authorized x-systems from database.

    Args:
        user_database: database dictionary
        api_key: API key to check

    Returns:
        optional list of authorized x-systems
    """
    return user_database.get(api_key)


def get_current_authorized_x_systems(
    api_key: Annotated[str | None, Depends(X_API_KEY)]
) -> list[XSystem]:
    """Get the current authorized x-systems.

    Raises:
        HTTPException if no header is provided or no x-system is authorized

    Args:
        api_key: the API key for x-system lookup

    Settings:
        drop_user_database: checked for presence of api_key

    Returns:
        list of authorized x-systems
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication header X-API-Key.",
        )

    settings = DropSettings.get()
    user_database = settings.drop_user_database
    x_systems = get_authorized_x_systems(user_database, APIKey(api_key))

    if not x_systems:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="The provided API Key is not recognized.",
        )

    return x_systems


def is_authorized(x_system: XSystem, authorized_x_systems: list[XSystem]) -> bool:
    """Check if the provided x-system is in the authorized x-systems.

    Args:
        x_system: x-system to check
        authorized_x_systems: list of authorized x-systems

    Returns:
        True if x_system or `admin` is in the authorized_x_systems else False
    """
    if {"admin", x_system} & set(authorized_x_systems):
        return True
    return False
