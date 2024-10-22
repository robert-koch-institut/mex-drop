import reflex as rx

from mex.drop.files_io import ALLOWED_CONTENT_TYPES
from mex.drop.state import AppState, TempFile


def mex_drop_logo() -> rx.Component:
    """Return the mex-drop logo with icon and label.

    Returns:
        rx.Component: A component with style, event trigger and other props
    """
    return rx.hstack(
        rx.icon(
            "droplets",
            size=28,
        ),
        rx.heading(
            "MEx Drop",
            weight="medium",
            style={"user-select": "none"},
        ),
        custom_attrs={"data-testid": "drop-logo"},
    )


def uploaded_file_display() -> rx.Component:
    """Displays list of uploaded files from drop interface.

    Returns:
        rx.Component: A component with style, event trigger and other props
    """
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell("Selected File", width=260),
                rx.table.column_header_cell("Actions", width=120),
            ),
        ),
        rx.table.body(
            rx.foreach(
                AppState.temp_files,
                create_file_row,
            ),
        ),
        width="100%",
    )


def create_file_row(temp_file: TempFile) -> rx.Component:
    """Create table row for each uploaded file.

    Args:
        temp_file (TempFile): temporarily uploaded file

    Returns:
        rx.Component: A component with style, event trigger and other props
    """
    return rx.table.row(
        rx.table.row_header_cell(temp_file.title, width=280),
        rx.table.cell(
            rx.button(
                rx.icon(tag="trash-2"),
                color_scheme="red",
                on_click=lambda: AppState.cancel_upload(temp_file.title),  # type: ignore[arg-type,call-arg]
            ),
            width=100,
        ),
    )


def create_drag_and_drop() -> rx.Component:
    """Create card for drag and drop area for file selection."""
    return rx.card(
        rx.vstack(
            mex_drop_logo(),
            rx.divider(size="4"),
            rx.text("Please select and upload your files here.", size="2"),
            rx.upload(
                rx.vstack(
                    rx.icon(
                        "file-down",
                        size=30,
                    ),
                    rx.text(
                        "Drag and drop " "or click to select files",
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
                        color="var(--white-1)",
                        bg="royalblue",
                    ),
                    align="center",
                ),
                id="upload_one",
                max_files=100,
                border="1px dotted var(--accent-8)",
                padding="3em",
                on_drop=AppState.handle_upload(rx.upload_files(upload_id="upload_one")),  # type: ignore[call-arg]
            ),
            spacing="4",
        ),
        top="20vh",
        width="100%",
        height="100%",
        padding="15px",
        custom_attrs={"data-testid": "index-card"},
    )


def create_file_handling_card() -> rx.Component:
    """Create card for file handling and upload."""
    return rx.card(
        rx.vstack(
            rx.scroll_area(
                rx.flex(
                    uploaded_file_display(),
                ),
                type="always",
                scrollbars="vertical",
                height=287,
            ),
            rx.form.root(
                rx.hstack(
                    rx.input(
                        placeholder="API key",
                        max_length=50,
                        id="api_key",
                        required=True,
                    ),
                    rx.input(
                        placeholder="x-system",
                        max_length=50,
                        id="x-system",
                        required=True,
                    ),
                    rx.button(
                        "Submit",
                        type="submit",
                        width="20%",
                        color="var(--white)",
                        bg="royalblue",
                    ),
                ),
                on_submit=AppState.submit_data,
                reset_on_submit=False,
            ),
        ),
        top="20vh",
        width="100%",
        height="100%",
    )


def index() -> rx.Component:
    """Return the index for the drop app.

    Returns:
        rx.Component: A component with style, event trigger and other props
    """
    return rx.box(
        rx.center(
            rx.container(
                rx.hstack(
                    create_drag_and_drop(),
                    create_file_handling_card(),
                    top="50vh",
                    width="100%",
                )
            )
        ),
        background_color="var(--gray-2)",
        min_height="100vh",
    )
