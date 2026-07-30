from shiny import App, reactive, ui

app_ui = ui.page_fillable(
    ui.input_action_button("show", "Show toast"),
    {"class": "vh-100 d-flex justify-content-center align-items-center px-4"},
)


def server(input, output, session):
    @reactive.effect
    @reactive.event(input.show)
    def _():
        ui.show_toast("This is a toast notification!")


app = App(app_ui, server)
