## file: app.py
from time import sleep
from shiny import App, reactive, render, ui

app_ui = ui.page_fluid(
    ui.row(
        ui.column(6, ui.input_task_button("task_button", "Increase Number slowly")),
        ui.column(6, ui.output_text("counter").add_class("display-5 mb-0")),
        {"class": "vh-100 justify-content-center align-items-center px-5"},
    ).add_class("text-center")
)


def server(input, output, session):
    count = reactive.value(0)

    @reactive.effect
    @reactive.event(input.task_button)
    def _():
        sleep(1)
        count.set(count() + 1)

    @render.text
    def counter():
        return f"{count()}"


app = App(app_ui, server)
