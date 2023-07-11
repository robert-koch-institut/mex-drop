from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader
from starlette import status

from mex.drop.models.user import User
from mex.drop.settings import DropSettings
from mex.drop.types.user_database import UserDatabase

X_API_KEY = APIKeyHeader(name="X-API-Key")


def get_user(db: UserDatabase, username: str) -> User | None:
    """Get user from database.

    Args:
        db: database dictionary
        username: username

    Returns:
        User if username in db, else None
    """
    return db.get(username)


def get_current_user(api_key: Annotated[str, Depends(X_API_KEY)]) -> User:
    """Get the current user.

    Raises HTTPException if user is not present

    Args:
        api_key: the API key for user lookup

    Settings:
        drop_user_database: checked for presence of api_key

    Returns:
        User
    """
    settings = DropSettings.get()
    user_db = settings.drop_user_database

    user = get_user(user_db, api_key)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
            headers={"X-API-Key": ""},
        )
    return user
