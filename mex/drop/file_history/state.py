import pathlib
from datetime import UTC, datetime

import reflex as rx

from mex.drop.settings import DropSettings
from mex.drop.state import State


class ListState(State):
    """The state for the file history page."""

    file_list: list[dict] = []

    def get_uploaded_files(self) -> EventSpec | None:
        """Get the list of files uploaded by the user to X System."""
        from typing import cast
        cast(State, State).check_login()
        if not self.user:
            return rx.toast.error("No User logged in.", close_button=True)
        settings = DropSettings.get()
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
