from faicons import icon_svg
from shiny import App, ui

app_ui = ui.page_fixed(
    ui.card(
        ui.card_header(
            "Left-Aligned Toolbar",
            ui.toolbar(
                ui.toolbar_input_button(
                    id="undo",
                    label="Undo",
                    icon=icon_svg("rotate-left"),
                ),
                ui.toolbar_input_button(
                    id="redo",
                    label="Redo",
                    icon=icon_svg("rotate-right"),
                ),
                align="left",
            ),
        ),
        ui.card_body(
            ui.p("Toolbar aligned to the left side of the header."),
        ),
        full_screen=True,
    )
)


def server(input, output, session):
    pass


app = App(app_ui, server)
