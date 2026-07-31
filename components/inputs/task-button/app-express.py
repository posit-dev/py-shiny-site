import time

from shiny import reactive, render
from shiny.express import input, ui

ui.input_task_button("task_button", "Run task")  # <<


@render.code
@reactive.event(input.task_button)
def result():
    time.sleep(2)  # Simulate a long-running task
    return f"Task completed {input.task_button()} time(s)"
