from faicons import icon_svg
from shiny import App, ui

app_ui = ui.page_fixed(
    ui.card(
        ui.card_header(
            "Project Dashboard",
            ui.toolbar(
                ui.toolbar_input_button(
                    id="refresh",
                    label="Refresh",
                    icon=icon_svg("arrows-rotate"),
                ),
                ui.toolbar_divider(),
                ui.toolbar_input_select(
                    id="filter",
                    label="Filter",
                    choices=["All", "Active", "Completed"],
                    icon=icon_svg("filter"),
                ),
                align="right",
            ),
        ),
        ui.card_body(
            ui.p("Toolbar with buttons, selects, and dividers."),
        ),
        full_screen=True,
    )
)


def server(input, output, session):
    pass


app = App(app_ui, server)
