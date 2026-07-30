from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.input_code_editor("code", "Enter Python code:", "print('Hello, world!')", language="python"),  # <<
    ui.output_code("value"),
)


def server(input, output, session):
    @render.code
    def value():
        return input.code()


app = App(app_ui, server)
