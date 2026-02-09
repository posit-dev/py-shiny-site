from faicons import icon_svg
from shiny import App, ui

app_ui = ui.page_fixed(
    ui.card(
        ui.card_header(
            "Document Editor",
            ui.toolbar(
                ui.toolbar_input_button(
                    id="save",
                    label="Save",
                    icon=icon_svg("floppy-disk"),
                ),
                ui.toolbar_input_button(
                    id="edit",
                    label="Edit",
                    icon=icon_svg("pencil"),
                ),
                align="right",
            ),
        ),
        ui.card_body(
            ui.p("Click the toolbar buttons to perform actions."),
        ),
        full_screen=True,
    )
)


def server(input, output, session):
    pass


app = App(app_ui, server)
