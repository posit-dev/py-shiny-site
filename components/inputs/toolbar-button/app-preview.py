from faicons import icon_svg
from shiny import App, ui

app_ui = ui.page_fluid(
    ui.card(
        ui.card_header(
            "Card",
            ui.toolbar(
                ui.toolbar_input_button(
                    id="label_only",
                    label="Label Button",
                ),
                ui.toolbar_input_button(
                    id="icon_only",
                    label="Icon Button",
                    icon=icon_svg("floppy-disk"),
                ),
                align="right",
            ),
        ),
        ui.card_body(
            ui.div("Card body", class_="small"),
        ),
    ),
    {"class": "vh-100 d-flex justify-content-center align-items-center px-4"},
)


def server(input, output, session):
    pass


app = App(app_ui, server)
