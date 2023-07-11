from pydantic import BaseModel


class User(BaseModel):
    """User model."""

    username: str
    x_system: str
