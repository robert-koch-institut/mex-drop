from typing import Annotated, Any

from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from starlette import status

X_API_KEY = APIKeyHeader(name="X-API-Key")


FAKE_USERS_DB = {
    "johndoe": {
        "username": "johndoe",
        "x_system": "test_system",
    },
    "alice": {
        "username": "alice",
        "x_system": "foo_system",
    },
}


class User(BaseModel):
    """User model."""

    username: str
    x_system: str


def get_user(db: dict[str, Any], username: str) -> User | None:
    """Get user from database.

    Args:
        db: database dictionary
        username: user name

    Returns:
        User if username in db, else None
    """
    if username in db:
        user_dict = db[username]
        return User(**user_dict)
    else:
        return None


def get_current_user(api_key: Annotated[str, Depends(X_API_KEY)]) -> User:
    """Get the current user.

    Raises HTTPException if user is not present

    Args:
        api_key: the API key for user lookup

    Returns:
        User
    """
    user = get_user(FAKE_USERS_DB, api_key)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
            headers={"X-API-Key": ""},
        )
    return user
