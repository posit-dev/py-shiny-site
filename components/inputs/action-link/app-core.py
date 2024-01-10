from shiny import App, reactive, render, ui

app_ui = ui.page_fluid(
    ui.input_action_link("action_link", "Action"),  # <<
    ui.output_text("counter"),
)


def server(input, output, session):
    @render.text()
    @reactive.event(input.action_link)
    def counter():
        return f"{input.action_link()}"


app = App(app_ui, server)
