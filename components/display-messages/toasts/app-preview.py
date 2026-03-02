from shiny import ui, reactive, App

app_ui = ui.page_fluid(
    ui.input_action_button("show", "Show Toast"),
)

def server(input, output, session):
    @reactive.effect
    @reactive.event(input.show)
    def _():
        ui.show_toast("This is a toast notification!")

app = App(app_ui, server)
