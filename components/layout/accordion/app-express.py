from shiny.express import input, render, ui

with ui.accordion(id="acc", open=["Section A"]):  # <<
    with ui.accordion_panel("Section A"):
        "Some narrative for section A"
    with ui.accordion_panel("Section B"):
        "Some narrative for section B"
    with ui.accordion_panel("Section C"):
        "Some narrative for section C"


@render.code
def selected():
    return f"Open panel(s): {input.acc()}"
