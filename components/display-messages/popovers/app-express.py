from shiny.express import input, render, ui

with ui.popover(id="btn_popover", title="A popover", placement="right"):  # <<
    ui.input_action_button("btn", "A button with a popover")  # <<
    "A message inside the popover."  # <<


@render.code
def popover_state():
    return f"Popover state: {input.btn_popover()}"  # <<
