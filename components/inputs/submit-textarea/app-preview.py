from shiny import App, ui

app_ui = ui.page_fluid(
    ui.input_submit_textarea(
        "message",
        "",
        placeholder="Type a message...",
    ),
    {"class": "vh-100 d-flex justify-content-center align-items-center px-4"},
)


def server(input, output, session):
    pass


app = App(app_ui, server)
