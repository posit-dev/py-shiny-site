from shiny import reactive
from shiny.express import input, render, ui

ui.input_action_link("action_link", "Increase Number")  # <<


count = reactive.value(0)


@reactive.effect
@reactive.event(input.action_link)
def _():
    count.set(count() + 1)


@render.text()
def counter():
    return f"{count()}"
