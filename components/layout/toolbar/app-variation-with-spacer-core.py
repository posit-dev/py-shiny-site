from faicons import icon_svg
from shiny import App, ui

app_ui = ui.page_fixed(
    ui.card(
        ui.card_header(
            "Split Toolbar",
            ui.toolbar(
                ui.toolbar_input_button(
                    id="back",
                    label="Back",
                    icon=icon_svg("arrow-left"),
                ),
                ui.toolbar_spacer(),
                ui.toolbar_input_button(
                    id="help",
                    label="Help",
                    icon=icon_svg("arrow-right"),
                ),
                align="left",
                width="100%",
            ),
        ),
        ui.card_body(
            ui.p("Toolbar spacer pushes buttons to opposite ends."),
        ),
        full_screen=True,
    )
)


def server(input, output, session):
    pass


app = App(app_ui, server)
