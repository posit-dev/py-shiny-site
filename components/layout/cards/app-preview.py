from shiny import App, render, ui

app_ui = ui.page_fixed(
    ui.card(
        ui.card_header(
            "Sales Overview",
            class_="bg-dark",
        ),
        ui.card_body(
            ui.output_text("contents"),
        ),
        max_height="400px",
        full_screen=True,
        id="card",
    ),
    {"class": "vh-100 d-flex justify-content-center align-items-center px-4"},
)


def server(input, output, session):
    @render.text
    def contents():
        if input.card_full_screen():
            return "Card contents, now in full screen."
        return "Card contents."


app = App(app_ui, server)
