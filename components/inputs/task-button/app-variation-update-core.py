import time

from shiny import App, reactive, render, ui

app_ui = ui.page_fluid(
    ui.input_task_button("run", "Run task", auto_reset=False),  # <<
    ui.input_action_button("reset", "Reset task button"),
    ui.output_code("result"),
)


def server(input, output, session):
    @render.code
    @reactive.event(input.run)
    def result():
        time.sleep(1.5)  # Simulate a long-running task
        return f"Task completed {input.run()} time(s)"

    @reactive.effect
    @reactive.event(input.reset)
    def _():
        ui.update_task_button("run", state="ready")  # <<


app = App(app_ui, server)
