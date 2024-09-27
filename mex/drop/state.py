import pathlib
from typing import Any

import reflex as rx
from reflex.event import EventSpec

from mex.drop.files_io import write_to_file
from mex.drop.security import get_current_authorized_x_systems, is_authorized
from mex.drop.settings import DropSettings


class TempFile(rx.Base):  # type: ignore
    """Helper class to handle temporarily uplaoded files."""

    title: str
    content: bytes


class AppState(rx.State):  # type: ignore
    """The app state."""

    temp_files: list[TempFile] = []
    form_data: dict[str, str] = {}

    @classmethod
    def get_instance(cls) -> Any:
        """Get the instance of the class."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def handle_upload(self, files: list[rx.UploadFile]) -> EventSpec | None:
        """Handle the upload of file(s) and save to temporary file list.

        Args:
            files: The uploaded file(s).
        """
        for file in files:
            if any(item.title == str(file.filename) for item in self.temp_files):
                return rx.toast.error(
                    "Duplicate filename. "
                    "Please make sure "
                    "to not upload the same file twice."
                )
            content = await file.read()
            self.temp_files.append(TempFile(title=str(file.filename), content=content))
        return None

    async def submit_data(self, form_data: dict[str, str]) -> EventSpec:
        """Submit temporarily uplaoded file(s) and save in corresponding directory.

        Args:
            form_data (dict[str, str]): api token and x sysem from input field
        """
        self.form_data = form_data
        x_system = form_data.get("x_system")
        api_token = form_data.get("api_token")
        authorized_x_systems = get_current_authorized_x_systems(api_key=api_token)

        if not is_authorized(str(x_system), authorized_x_systems):
            return rx.toast.error(
                "API Key not authorized to drop data for this x_system.",
                close_button=True,
            )

        if not self.temp_files:
            return rx.toast.error("No files to upload.", close_button=True)

        settings = DropSettings.get()
        for file in self.temp_files:
            entity_type = str(file.title)
            out_file = pathlib.Path(settings.drop_directory, str(x_system), entity_type)
            await write_to_file(file.content, out_file)

        self.temp_files.clear()
        return rx.toast.success("File upload successful!")

    def cancel_upload(self, filename: str) -> EventSpec:
        """Delete file from temporary file list.

        Args:
            filename (str): title of file to be deleted
        """
        self.temp_files = [file for file in self.temp_files if file.title != filename]
        return rx.toast.info(f"File {filename} removed from upload.")
