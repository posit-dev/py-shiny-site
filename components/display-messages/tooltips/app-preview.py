from shiny import render
from shiny.express import input, ui

with ui.tooltip(id="btn_tooltip", placement="right"):  # <<
    ui.input_action_button("btn", "A button with a tooltip")  # <<
    "The tooltip message"  # <<


@render.text
def btn_tooltip_state():
    return f"Tooltip state: {input.btn_tooltip()}"  # <<
