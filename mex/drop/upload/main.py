import reflex as rx

from mex.drop.layout import page
from mex.drop.upload.models import TempFile
from mex.drop.upload.state import UploadState


def uploaded_file_display() -> rx.Component:
    """Displays list of uploaded files from drop interface."""
    return rx.scroll_area(
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell(
                        UploadState.label_file_table_selected_file_column,
                        style=rx.Style(width="80%"),
                    ),
                    rx.table.column_header_cell(
                        UploadState.label_file_table_action_column,
                    ),
                ),
            ),
            rx.table.body(
                rx.foreach(
                    UploadState.temp_files,
                    create_file_row,
                ),
            ),
        ),
        type="hover",
        scrollbars="both",
        style=rx.Style(width="100%", height="100%"),
    )


def create_file_row(temp_file: TempFile) -> rx.Component:
    """Create table row for each uploaded file.

    Args:
        temp_file: temporarily uploaded file
    """
    return rx.table.row(
        rx.table.row_header_cell(temp_file.title),
        rx.table.cell(
            rx.button(
                rx.icon(tag="trash-2"),
                title=UploadState.label_file_table_remove_button,
                color_scheme="tomato",
                variant="ghost",
                custom_attrs={"data-testid": "remove-file-button"},
                on_click=UploadState.cancel_upload(temp_file.title),  # type: ignore[operator]
            ),
            style=rx.Style(width="100%"),
        ),
    )


def create_drag_and_drop() -> rx.Component:
    """Create card for drag and drop area for file selection."""
    return rx.card(
        rx.vstack(
            rx.text(
                UploadState.label_drag_and_drop_title,
                size="2",
                weight="bold",
                style=rx.Style(
                    padding="calc(12px * var(--scaling)) calc(12px * var(--scaling)) 0;"
                ),
            ),
            rx.divider(size="4"),
            rx.upload(
                rx.vstack(
                    rx.icon(
                        "file-down",
                        size=28,
                    ),
                    rx.text(
                        UploadState.label_drag_and_drop_hint,
                        size="1",
                    ),
                    rx.text(
                        UploadState.label_drag_and_drop_supported_formats_format,
                        size="1",
                        color_scheme="gray",
                    ),
                    rx.button(
                        UploadState.label_drag_and_drop_select_button,
                        variant="surface",
                        custom_attrs={"data-testid": "select-files-button"},
                    ),
                    align="center",
                ),
                id="file_upload_area",
                max_files=100,
                style=rx.Style(
                    border="var(--card-border-width) dotted var(--accent-8)",
                    borderRadius="calc(var(--base-card-border-radius) - var(--base-card-border-width))",  # noqa: E501
                    padding="var(--space-4)",
                    margin="var(--space-8) auto",
                ),
                on_drop=UploadState.handle_upload(  # type: ignore[operator]
                    rx.upload_files(upload_id="file_upload_area")
                ),
            ),
            spacing="3",
        ),
        style=rx.Style(width="100%", height="100%"),
    )


def create_file_handling_card() -> rx.Component:
    """Create card for file handling and upload."""
    return rx.card(
        rx.vstack(
            uploaded_file_display(),
            rx.hstack(
                rx.spacer(spacing="3"),
                rx.button(
                    UploadState.label_submit_button,
                    on_click=UploadState.submit_data,
                    color_scheme="jade",
                    custom_attrs={"data-testid": "submit-button"},
                ),
                style=rx.Style(width="100%"),
            ),
            style=rx.Style(height="100%"),
        ),
        style=rx.Style(width="100%", height="100%"),
    )


def index() -> rx.Component:
    """Return the index for the upload component."""
    return page(
        rx.hstack(
            create_drag_and_drop(),
            create_file_handling_card(),
            spacing="6",
            style=rx.Style(width="100%", height="calc(480px * var(--scaling))"),
        )
    )
