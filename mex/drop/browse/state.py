import pathlib
from datetime import UTC, datetime

import reflex as rx
from reflex.event import EventSpec

from mex.drop.browse.models import FileDetails
from mex.drop.label_var import label_var
from mex.drop.settings import DropSettings
from mex.drop.state import State


class BrowseState(State):
    """The state for the browse page."""

    file_list: list[FileDetails] = []

    @label_var(label_id="browse.file_table.name_column")
    def label_file_table_name_column(self) -> None:
        """Label for file_table.name_column."""

    @label_var(label_id="browse.file_table.created_column")
    def label_file_table_created_column(self) -> None:
        """Label for file_table.created_column."""

    @label_var(label_id="browse.file_table.modified_column")
    def label_file_table_modified_column(self) -> None:
        """Label for file_table.modified_column."""

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
        self.file_list.clear()
        if x_system_data_dir.is_dir():
            for file in x_system_data_dir.glob("*"):
                if file.is_file():
                    file_stat = file.stat()
                    self.file_list.append(
                        FileDetails(
                            name=file.name,
                            created=datetime.fromtimestamp(
                                file_stat.st_ctime, tz=UTC
                            ).strftime("%d-%m-%Y %H:%M:%S"),
                            modified=datetime.fromtimestamp(
                                file_stat.st_mtime, tz=UTC
                            ).strftime("%d-%m-%Y %H:%M:%S"),
                        )
                    )
            return None
        return rx.toast.error(
            self._locale_service.get_ui_label(
                self.current_locale, "browse.x_system_not_found"
            ),
            close_button=True,
        )
