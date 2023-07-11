from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from starlette import status

X_API_KEY = APIKeyHeader(name="X-API-Key")


class User(BaseModel):
    """User model."""

    username: str
    x_system: str


UserDatabase = dict[str, User]


FAKE_USERS_DB: UserDatabase = {
    k: User(**v)
    for k, v in {
        "johndoe": {
            "username": "johndoe",
            "x_system": "test_system",
        },
        "alice": {
            "username": "alice",
            "x_system": "foo_system",
        },
    }.items()
}


def get_user(db: UserDatabase, username: str) -> User | None:
    """Get user from database.

    Args:
        db: database dictionary
        username: user name

    Returns:
        User if username in db, else None
    """
    if username in db:
        return db[username]
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
