from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.input_date_range("x", ""),
    ui.output_code("txt"),
    {"class": "vh-100 d-flex justify-content-center align-items-center px-4"},
)


def server(input, output, session):
    @render.code
    def txt():
        return ""


app = App(app_ui, server, debug=True)
