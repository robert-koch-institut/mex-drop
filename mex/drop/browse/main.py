import reflex as rx

from mex.drop.browse.models import FileDetails
from mex.drop.browse.state import BrowseState
from mex.drop.layout import page


def render_file_row(file: FileDetails) -> rx.Component:
    """Render a row for the browse display."""
    return rx.table.row(
        rx.table.row_header_cell(file.name),
        rx.table.cell(f"{file.created}"),
        rx.table.cell(f"{file.modified}"),
    )


def uploaded_files_display() -> rx.Component:
    """Display the uploaded files."""
    return rx.center(
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell(
                        BrowseState.label_file_table_name_column
                    ),
                    rx.table.column_header_cell(
                        BrowseState.label_file_table_created_column
                    ),
                    rx.table.column_header_cell(
                        BrowseState.label_file_table_modified_column
                    ),
                ),
            ),
            rx.table.body(
                rx.foreach(
                    BrowseState.file_list,
                    render_file_row,
                ),
            ),
            width="100%",
        ),
        width="100%",
    )


def index() -> rx.Component:
    """Return the index for the browse component."""
    return page(
        rx.card(
            rx.vstack(
                rx.scroll_area(
                    rx.flex(
                        uploaded_files_display(),
                    ),
                    type="hover",
                    scrollbars="vertical",
                ),
            ),
            custom_attrs={"data-testid": "index-card"},
            style=rx.Style(
                width="100%",
                minHeight="calc(480px * var(--scaling))",
            ),
        ),
    )
