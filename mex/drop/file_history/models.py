import reflex as rx


class FileDetails(rx.Base):
    """Class to describe file details."""

    name: str
    created: str
    modified: str
