from faicons import icon_svg
from shiny import App, ui

app_ui = ui.page_fixed(
    ui.card(
        ui.card_header(
            ui.span("Card", class_="text-body-secondary fw-normal"),
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
        ui.card_body(
            ui.div("Card contents", class_="small text-body-secondary"),
        ),
        height="7rem",
        style="width: 16rem;",
    ),
    {"class": "vh-100 d-flex justify-content-center align-items-center px-4"},
)


def server(input, output, session):
    pass


app = App(app_ui, server)
