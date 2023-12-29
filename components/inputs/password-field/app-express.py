# FIXME: Rewrite as an Express app
from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.input_password("password", "Password", "mypassword1"), #<<
    ui.output_text_verbatim("value"),
)

def server(input, output, session):
    @render.text
    def value():
        return input.password()

app = App(app_ui, server)
