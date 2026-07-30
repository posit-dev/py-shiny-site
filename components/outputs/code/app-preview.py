from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.input_text("message", "", placeholder="Enter a message"),
    ui.output_code("code", placeholder=True),
    {
        "class": "vh-100 d-flex justify-content-center align-items-center flex-column px-4"
    },
)


def server(input, output, session):
    @render.code
    def code():
        return f'print("{input.message()}")'


app = App(app_ui, server)
