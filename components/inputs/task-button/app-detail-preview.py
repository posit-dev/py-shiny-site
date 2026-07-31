import time

from shiny import App, reactive, render, ui

app_ui = ui.page_fluid(
    ui.row(
        ui.column(6, ui.input_task_button("task_button", "Run task")),
        ui.column(6, ui.output_code("result")),
        {"class": "vh-100 justify-content-center align-items-center px-5"},
    ).add_class("text-center")
)


def server(input, output, session):
    @render.code
    @reactive.event(input.task_button)
    def result():
        time.sleep(1.5)  # Simulate a long-running task
        return f"Ran {input.task_button()} time(s)"


app = App(app_ui, server)
