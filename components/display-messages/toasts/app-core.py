from shiny import ui, reactive, App

app_ui = ui.page_fluid(
    ui.input_action_button("show", "Show toast"),
)

def server(input, output, session):
    @reactive.effect
    @reactive.event(input.show)
    def _():
        ui.show_toast("Hello! This is a toast message.") # <<

app = App(app_ui, server)
