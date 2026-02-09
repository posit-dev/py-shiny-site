from shiny import App, ui

app_ui = ui.page_fixed(
    ui.card(
        ui.card_header(
            "Sales Overview",
            class_="bg-dark",
        ),
        ui.card_body(
            ui.p("This card displays key sales metrics and trends."),
            ui.p("Track monthly performance and year-over-year growth.")
        ),
        max_height="400px",
        full_screen=True,
    )
)


def server(input, output, session):
    pass


app = App(app_ui, server)
