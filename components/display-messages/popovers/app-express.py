from shiny.express import input, render, ui

with ui.popover(id="btn_popover", title="Popover Title", placement="right"):  # <<
    ui.input_action_button("btn", "Click for popover")  # <<
    "A popover provides additional context and interactive elements."  # <<


@render.text
def btn_popover_state():
    return f"Popover open state: {input.btn_popover()}"  # <<
