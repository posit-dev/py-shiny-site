import time

from shiny import App, reactive, render, ui

app_ui = ui.page_fluid(
    ui.input_task_button("task_button", "Run task"),  # <<
    ui.output_text("result"),
)


def server(input, output, session):
    @render.text
    @reactive.event(input.task_button)
    def result():
        time.sleep(2)
        return f"Task completed {input.task_button()} time(s)"


app = App(app_ui, server)
