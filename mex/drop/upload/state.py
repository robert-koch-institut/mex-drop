import pathlib

import reflex as rx
from reflex.event import EventSpec

from mex.drop.files_io import ALLOWED_CONTENT_TYPES, write_to_file
from mex.drop.label_var import label_var
from mex.drop.settings import DropSettings
from mex.drop.state import State
from mex.drop.upload.models import TempFile


class UploadState(State):
    """The state for the upload page."""

    temp_files: list[TempFile] = []

    @label_var(label_id="upload.drag_and_drop.title")
    def label_drag_and_drop_title(self) -> None:
        """Label for drag_and_drop.title."""

    @label_var(label_id="upload.drag_and_drop.hint")
    def label_drag_and_drop_hint(self) -> None:
        """Label for drag_and_drop.hint."""

    @label_var(label_id="upload.drag_and_drop.supported_formats.format")
    def label_drag_and_drop_supported_formats_format(self) -> list[str]:
        """Label for drag_and_drop.supported_formats.format."""
        return [", ".join(ALLOWED_CONTENT_TYPES.values())]

    @label_var(label_id="upload.drag_and_drop.select_button")
    def label_drag_and_drop_select_button(self) -> None:
        """Label for drag_and_drop.select_button."""

    @label_var(label_id="upload.file_table.selected_file_column")
    def label_file_table_selected_file_column(self) -> None:
        """Label for file_table.selected_file_column."""

    @label_var(label_id="upload.file_table.action_column")
    def label_file_table_action_column(self) -> None:
        """Label for file_table.action_column."""

    @label_var(label_id="upload.file_table.remove_button")
    def label_file_table_remove_button(self) -> None:
        """Label for file_table.remove_button."""

    @label_var(label_id="upload.submit_button")
    def label_submit_button(self) -> None:
        """Label for submit_button."""

    @rx.event
    async def handle_upload(self, files: list[rx.UploadFile]) -> EventSpec | None:
        """Handle the upload of file(s) and save them to the temporary file list.

        Args:
            files: The list of uploaded files to be processed.

        Returns:
            EventSpec | None: Returns EventSpec with error toast message if duplicate
            filename is found. Otherwise, returns None.
        """
        for file in files:
            if file.content_type not in ALLOWED_CONTENT_TYPES:
                return rx.toast.error(
                    self._locale_service.get_ui_label(
                        self.current_locale, "upload.unsupported_format.format"
                    ).format(", ".join(ALLOWED_CONTENT_TYPES.values())),
                    close_button=True,
                )
            if any(item.title == str(file.name) for item in self.temp_files):
                return rx.toast.error(
                    self._locale_service.get_ui_label(
                        self.current_locale, "upload.duplicate_filename"
                    )
                )
            content = await file.read()
            self.temp_files.append(TempFile(title=str(file.name), content=content))
        return None

    @rx.event
    async def submit_data(self) -> EventSpec:
        """Submit temporarily uploaded file(s) and save in corresponding directory.

        Returns:
            EventSpec: Reflex event, toast info message
        """
        if not self.temp_files:
            return rx.toast.error(
                self._locale_service.get_ui_label(
                    self.current_locale, "upload.no_files_to_upload"
                ),
                close_button=True,
            )

        if not self.user:
            return rx.toast.error(
                self._locale_service.get_ui_label(
                    self.current_locale, "upload.no_user_logged_in"
                ),
                close_button=True,
            )

        settings = DropSettings.get()
        for file in self.temp_files:
            entity_type = str(file.title)
            out_file = pathlib.Path(
                settings.drop_directory, str(self.user.x_system), entity_type
            )
            await write_to_file(file.content, out_file)

        self.temp_files.clear()
        return rx.toast.success(
            self._locale_service.get_ui_label(
                self.current_locale, "upload.upload_successful"
            )
        )

    @rx.event
    def cancel_upload(self, filename: str) -> EventSpec:
        """Delete file from temporary file list.

        Args:
            filename: title of file to be deleted

        Returns:
            EventSpec: Reflex event, toast info message
        """
        self.temp_files = [file for file in self.temp_files if file.title != filename]
        return rx.toast.info(
            self._locale_service.get_ui_label(
                self.current_locale, "upload.file_removed.format"
            ).format(filename)
        )
