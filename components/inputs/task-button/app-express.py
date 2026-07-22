import time

from shiny import reactive, render
from shiny.express import input, ui

ui.input_task_button("task_button", "Run task")  # <<


@render.text
@reactive.event(input.task_button)
def result():
    time.sleep(2)
    return f"Task completed {input.task_button()} time(s)"
