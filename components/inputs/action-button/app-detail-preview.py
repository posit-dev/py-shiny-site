## file: app.py
from shiny import App, reactive, render, ui

app_ui = ui.page_fluid(
    ui.row(
        ui.column(6, ui.input_action_button("action_button", "Increase Number")),
        ui.column(6, ui.output_text("counter").add_class("display-5 mb-0")),
        {"class": "vh-100 justify-content-center align-items-center px-5"},
    ).add_class("text-center")
)


def server(input, output, session, starting_value=0):
    count = reactive.Value(starting_value)

    @reactive.Effect
    @reactive.event(input.action_button)
    def _():
        count.set(count() + 1)

    @render.text
    def counter():
        return f"{count()}"


app = App(app_ui, server)
