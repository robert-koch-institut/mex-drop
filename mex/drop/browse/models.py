from pydantic import BaseModel


class FileDetails(BaseModel):
    """Class to describe file details."""

    name: str
    created: str
    modified: str
