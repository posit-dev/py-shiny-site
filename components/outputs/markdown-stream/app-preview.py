from shiny import ui, App

app_ui = ui.page_fluid(
    ui.output_markdown_stream("stream"),
)

def server(input, output, session):
    pass

app = App(app_ui, server)
