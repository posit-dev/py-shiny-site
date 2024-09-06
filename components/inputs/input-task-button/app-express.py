from time import sleep

from shiny import reactive
from shiny.express import input, render, ui

with ui.sidebar():
    ui.input_task_button("task_button", "Increase Number slowly")  # <<


@render.text
def counter():
    return f"{count()}"


count = reactive.value(0)


@reactive.effect  # <<
@reactive.event(input.task_button)  # <<
def _():
    sleep(1)
    count.set(count() + 1)
