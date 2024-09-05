from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.input_text("x", "", placeholder="Enter text"),
    ui.output_text_verbatim("txt"),
    {
        "class": "vh-100 d-flex justify-content-center align-items-center flex-column px-4"
    },
)


def server(input, output, session):
    @output
    @render.text
    def txt():
        return f'x: "{input.x()}"'


app = App(app_ui, server, debug=True)
