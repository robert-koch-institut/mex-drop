import reflex as rx


def mex_drop_logo() -> rx.Component:
    """Return the mex-drop logo with icon and label."""
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
    """Displays uploaded files from drop interface."""
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell("Uploaded File", width="80%"),
                rx.table.column_header_cell("Actions", width="20%"),
            ),
        ),
        rx.table.body(
            rx.table.row(
                rx.table.row_header_cell("Test_File.xml", width="80%"),
                rx.table.cell(
                    rx.button(
                        rx.icon(tag="trash-2"),
                        color_scheme="red",
                    ),
                    width="20%",
                ),
            )
        ),
        width="90%",
    )


def index() -> rx.Component:
    """Return the index for the drop app."""
    return rx.center(
        rx.container(
            rx.hstack(
                rx.card(
                    rx.vstack(
                        mex_drop_logo(),
                        rx.divider(size="4"),
                        rx.text(
                            "Upload your files here.",
                        ),
                        rx.upload(
                            rx.vstack(
                                rx.icon("file-down"),
                                rx.text(
                                    "Drag and drop files here or click to select files"
                                ),
                                rx.button(
                                    "Select File",
                                    color="rgb(107,99,246)",
                                    bg="white",
                                    border="1px solid rgb(107,99,246)",
                                ),
                                align="center",
                            ),
                            border="1px dotted rgb(107,99,246)",
                            padding="10em",
                        ),
                        spacing="4",
                    ),
                    top="20vh",
                    width="50%",
                    variant="classic",
                    custom_attrs={"data-testid": "index-card"},
                ),
                rx.card(
                    rx.vstack(
                        uploaded_file_display(),
                        rx.hstack(
                            rx.input(
                                placeholder="API token",
                                max_length=50,
                                id="x-system-input",
                            ),
                            rx.input(
                                placeholder="x-system",
                                max_length=50,
                                id="x-system-input",
                            ),
                            rx.button("Submit", width="20%", id="submit-button"),
                        ),
                    ),
                    width="50%",
                    top="20vh",
                ),
                top="20vh",
                width="90%",
            ),
        )
    )
