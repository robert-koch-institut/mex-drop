import secrets
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader
from starlette import status

from mex.drop.settings import DropSettings
from mex.drop.types.user_database import UserDatabase

X_API_KEY = APIKeyHeader(name="X-API-Key")


def get_authorized_x_systems(db: UserDatabase, api_token: str) -> list[str]:
    """Get authorized x-systems from database.

    Args:
        db: database dictionary
        api_token: API token

    Returns:
        list of authorized x-systems
    """
    return db.get(api_token, [])


def get_current_authorized_x_systems(
    api_key: Annotated[str, Depends(X_API_KEY)]
) -> list[str]:
    """Get the current authorized x-systems.

    Raises HTTPException if user is not present

    Args:
        api_key: the API key for x-system lookup

    Settings:
        drop_user_database: checked for presence of api_key

    Returns:
        list of x-systems
    """
    settings = DropSettings.get()
    user_db = settings.drop_user_database

    x_systems = get_authorized_x_systems(user_db, api_key)
    if not x_systems:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
            headers={"X-API-Key": ""},
        )
    return x_systems


def generate_token() -> None:
    """Generate a token."""
    print(secrets.token_urlsafe())
