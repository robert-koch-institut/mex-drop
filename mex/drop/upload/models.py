from pydantic import BaseModel


class TempFile(BaseModel):
    """Helper class to handle temporarily uploaded files."""

    title: str
    content: bytes
