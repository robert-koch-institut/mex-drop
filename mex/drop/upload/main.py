from typing import cast

import reflex as rx

from mex.drop.files_io import ALLOWED_CONTENT_TYPES
from mex.drop.layout import page
from mex.drop.upload.state import AppState, TempFile


def uploaded_file_display() -> rx.Component:
    """Displays list of uploaded files from drop interface."""
    return rx.scroll_area(
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell(
                        "Selected File",
                        style={"width": "80%"},
                    ),
                    rx.table.column_header_cell(
                        "Action",
                    ),
                ),
            ),
            rx.table.body(
                rx.foreach(
                    AppState.temp_files,
                    create_file_row,
                ),
            ),
        ),
        type="hover",
        scrollbars="both",
        style={
            "width": "100%",
            "height": "100%",
        },
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
                title="Remove file",
                color_scheme="tomato",
                variant="ghost",
                on_click=lambda: cast(AppState, AppState).cancel_upload(
                    temp_file.title
                ),
            ),
            style={"width": "100%"},
        ),
    )


def create_drag_and_drop() -> rx.Component:
    """Create card for drag and drop area for file selection."""
    return rx.card(
        rx.vstack(
            rx.text(
                "File Upload",
                size="2",
                weight="bold",
                style={
                    "padding": "calc(12px * var(--scaling)) "
                    "calc(12px * var(--scaling)) 0;"
                },
            ),
            rx.divider(size="4"),
            rx.upload(
                rx.vstack(
                    rx.icon(
                        "file-down",
                        size=28,
                    ),
                    rx.text(
                        "Drag and drop or click to select files",
                        size="1",
                    ),
                    rx.text(
                        f"Supported formats: "
                        f"{', '.join(ALLOWED_CONTENT_TYPES.values())}",
                        size="1",
                        color_scheme="gray",
                    ),
                    rx.button(
                        "Select Files",
                        variant="surface",
                    ),
                    align="center",
                ),
                id="file_upload_area",
                max_files=100,
                style={
                    "border": "var(--card-border-width) dotted var(--accent-8)",
                    "borderRadius": "calc(var(--base-card-border-radius) - "
                    "var(--base-card-border-width))",
                    "padding": "var(--space-4)",
                    "margin": "var(--space-8) auto",
                },
                on_drop=cast(AppState, AppState).handle_upload(
                    rx.upload_files(upload_id="file_upload_area")
                ),
            ),
            spacing="3",
        ),
        style={
            "width": "100%",
            "height": "100%",
        },
    )


def create_file_handling_card() -> rx.Component:
    """Create card for file handling and upload."""
    return rx.card(
        rx.vstack(
            uploaded_file_display(),
            rx.hstack(
                rx.spacer(spacing="3"),
                rx.button(
                    "Submit",
                    on_click=AppState.submit_data,
                    color_scheme="jade",
                ),
                style={"width": "100%"},
            ),
            style={"height": "100%"},
        ),
        style={
            "width": "100%",
            "height": "100%",
        },
    )


def index() -> rx.Component:
    """Return the index for the upload component."""
    return page(
        rx.hstack(
            create_drag_and_drop(),
            create_file_handling_card(),
            style={
                "width": "100%",
                "height": "calc(480px * var(--scaling))",
            },
        )
    )
