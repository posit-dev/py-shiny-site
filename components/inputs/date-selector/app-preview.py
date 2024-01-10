from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.input_date("x", ""),
    ui.output_text_verbatim("txt"),
    {
        "class": "vh-100 d-flex justify-content-center align-items-center px-4 flex-column"
    },
)


def server(input, output, session):
    @render.text
    def txt():
        return ""


app = App(app_ui, server, debug=True)
