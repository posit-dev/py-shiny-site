from shiny import App, reactive, render, ui
app_ui = ui.page_fluid(
    ui.input_action_link("action_link", "Action"), 
    ui.output_text("counter"),
    {"class": "vh-100 d-flex justify-content-center align-items-center px-4"}
)
def server(input, output, session):
    @output
    @render.text()
    @reactive.event(input.action_link)
    def counter():
        return f""
app = App(app_ui, server)
