from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.input_slider("x", "", min=0, max=20, value=10),
    ui.output_text_verbatim("txt"),
    {"class": "vh-100 d-flex justify-content-center align-items-center px-4"},
)


def server(input, output, session):
    pass


app = App(app_ui, server, debug=True)
