import time

from shiny import App, reactive, render, ui

app_ui = ui.page_fluid(
    ui.input_task_button("task_button", "Run task"),  # <<
    ui.output_code("result"),
)


def server(input, output, session):
    @render.code
    @reactive.event(input.task_button)
    def result():
        time.sleep(2)  # Simulate a long-running task
        return f"Task completed {input.task_button()} time(s)"


app = App(app_ui, server)
