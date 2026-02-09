from faicons import icon_svg
from shiny import App, ui

app_ui = ui.page_fixed(
    ui.card(
        ui.card_header(
            "Data View",
            ui.toolbar(
                ui.toolbar_input_select(
                    id="view_mode",
                    label="View Mode",
                    choices=["Table", "Chart", "Map"],
                    icon=icon_svg("eye"),
                ),
                align="right",
            ),
        ),
        ui.card_body(
            ui.p("Select a view mode from the toolbar."),
        ),
        full_screen=True,
    )
)


def server(input, output, session):
    pass


app = App(app_ui, server)
