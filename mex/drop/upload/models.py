import reflex as rx


class TempFile(rx.Base):
    """Helper class to handle temporarily uploaded files."""

    title: str
    content: bytes
