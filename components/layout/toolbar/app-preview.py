from faicons import icon_svg
from shiny import App, ui

app_ui = ui.page_fixed(
    ui.card(
        ui.card_header(
            "Header",
            ui.toolbar(
                ui.toolbar_input_button(
                    id="action1",
                    label="Refresh",
                    icon=icon_svg("arrows-rotate"),
                ),
                ui.toolbar_divider(),
                ui.toolbar_input_select(
                    id="options",
                    label="Filter",
                    choices=["ABC", "CDE", "EFG"],
                ),
                align="right",
            ),
        ),
        ui.card_body(),
    ),
    {"class": "vh-100 d-flex justify-content-center align-items-center px-4"},
)


def server(input, output, session):
   pass


app = App(app_ui, server)
