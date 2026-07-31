import time

from shiny import reactive, render
from shiny.express import input, ui

ui.input_task_button("run", "Run task", auto_reset=False)  # <<
ui.input_action_button("reset", "Reset task button")


@render.code
@reactive.event(input.run)
def result():
    time.sleep(1.5)  # Simulate a long-running task
    return f"Task completed {input.run()} time(s)"


@reactive.effect
@reactive.event(input.reset)
def _():
    ui.update_task_button("run", state="ready")  # <<
