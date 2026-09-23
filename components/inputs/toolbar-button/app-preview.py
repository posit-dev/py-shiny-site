from faicons import icon_svg
from shiny import App, ui

app_ui = ui.page_fluid(
    ui.card(
        ui.card_header(
            "Card",
            ui.toolbar(
                ui.toolbar_input_button(
                    id="refresh",
                    label="Refresh",
                    icon=icon_svg("arrows-rotate"),
                ),
                ui.toolbar_input_button(
                    id="save",
                    label="Save",
                    icon=icon_svg("floppy-disk"),
                ),
                align="right",
            ),
        ),
        ui.card_body(
            ui.div("Card contents", class_="small"),
        ),
        height="7rem",
        style="width: 16rem;",
    ),
    {"class": "vh-100 d-flex justify-content-center align-items-center px-4"},
)


def server(input, output, session):
    pass


app = App(app_ui, server)
