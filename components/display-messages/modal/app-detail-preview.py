## file: app.py
from shiny import App, reactive, ui

app_ui = ui.page_fluid(
    ui.input_action_button("show", "Show modal dialog"),
)

def server(input, output, session):
    @reactive.Effect
    @reactive.event(input.show)
    def _():
        m = ui.modal(
            "This is a somewhat important message.",
            title="Somewhat important message",
            easy_close=True,
            footer=ui.modal_button("Dismiss"),
        )
        ui.modal_show(m)

app = App(app_ui, server)
