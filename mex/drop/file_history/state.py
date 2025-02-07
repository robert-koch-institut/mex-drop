import pathlib
from datetime import UTC, datetime

import reflex as rx
from reflex.event import EventSpec

from mex.drop.settings import DropSettings
from mex.drop.state import State


class ListState(State):
    """The state for the file history page."""

    file_list: list[dict] = []

    @rx.event
    def refresh(self) -> EventSpec | None:
        """Refresh the list of files uploaded by the user to X-System."""
        settings = DropSettings.get()
        if not self.user:  # pragma: no cover
            msg = "Should have redirected to login."
            raise RuntimeError(msg)
        x_system_data_dir = pathlib.Path(
            settings.drop_directory, str(self.user.x_system)
        )
        if not x_system_data_dir.is_dir():
            return rx.toast.error(
                "The requested x-system was not found on this server.",
                close_button=True,
            )
        file_details = []
        for file in x_system_data_dir.glob("*"):
            if file.is_file():
                file_stat = file.stat()

                file_details.append(
                    {
                        "name": file.name,
                        "created": datetime.fromtimestamp(
                            file_stat.st_ctime, tz=UTC
                        ).strftime("%d-%m-%Y %H:%M:%S"),
                        "modified": datetime.fromtimestamp(
                            file_stat.st_mtime, tz=UTC
                        ).strftime("%d-%m-%Y %H:%M:%S"),
                    }
                )
        self.file_list = file_details
        return None
