from shiny import App, ui

app_ui = ui.page_fixed(
    ui.card(
        ui.card_header(
            "Sales Overview",
            class_="bg-dark",
        ),
        ui.card_body(
            "This is a card body."
        ),
        max_height="400px",
        full_screen=True,
    ),
    {"class": "vh-100 d-flex justify-content-center align-items-center px-4"},
)


def server(input, output, session):
    pass


app = App(app_ui, server)
