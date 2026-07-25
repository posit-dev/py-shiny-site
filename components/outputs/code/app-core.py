from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.input_text("message", "Message", "Hello Shiny"),
    ui.output_code("code"),  # <<
)


def server(input, output, session):
    @render.code  # <<
    def code():
        return f'print("{input.message()}")'


app = App(app_ui, server)
