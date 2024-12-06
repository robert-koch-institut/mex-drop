import reflex as rx

from mex.drop.file_history.state import ListState
from mex.drop.navigation import nav_bar


def render_file_row(file: dict) -> rx.Component:
    """Render a row for the file history display."""
    return rx.table.row(
        rx.table.row_header_cell(file["name"]),
        rx.table.cell(f"{file['created']}"),
        rx.table.cell(f"{file['modified']}"),
    )


def uploaded_files_display() -> rx.Component:
    """Display the uploaded files."""
    return rx.center(
        rx.cond(
            ListState.file_list,
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("File Name"),
                        rx.table.column_header_cell("Created"),
                        rx.table.column_header_cell("Modified"),
                    ),
                ),
                rx.table.body(
                    rx.foreach(
                        ListState.file_list,
                        render_file_row,
                    ),
                ),
                width="100%",
            ),
        ),
        width="100%",
    )


def file_history_index() -> rx.Component:
    """Return the index for the file history page."""
    return rx.box(
        nav_bar(),
        rx.center(
            rx.card(
                rx.vstack(
                    rx.text("File Upload History", weight="bold", align="center"),
                    rx.divider(size="4"),
                    rx.scroll_area(
                        rx.flex(
                            uploaded_files_display(),
                        ),
                        type="always",
                        scrollbars="vertical",
                        height=350,
                    ),
                ),
                width="70%",
                padding="2em",
                margin="4em",
                custom_attrs={"data-testid": "index-card"},
            ),
        ),
        background_color="var(--gray-2)",
        height="100%",
        padding="2em",
    )
