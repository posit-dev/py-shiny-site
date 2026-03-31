from faicons import icon_svg
from shiny import App, ui

app_ui = ui.page_fixed(
    ui.card(
        ui.card_header(
            ui.toolbar(
                ui.toolbar_input_button(
                    id="left",
                    label="Left",
                    icon=icon_svg("arrow-left"),
                ),
                ui.toolbar_input_button(
                    id="right",
                    label="Right",
                    icon=icon_svg("arrow-right"),
                ),
                ui.toolbar_input_button(
                    id="refresh",
                    label="Refresh",
                    icon=icon_svg("arrows-rotate"),
                ),
                ui.toolbar_spacer(),
                ui.toolbar_input_button(
                    id="export",
                    label="Export",
                    icon=icon_svg("download"),
                ),
                ui.toolbar_input_button(
                    id="save",
                    label="Save",
                    icon=icon_svg("floppy-disk"),
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
