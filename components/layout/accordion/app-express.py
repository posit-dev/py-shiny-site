from shiny.express import input, render, ui

with ui.accordion(id="acc", open=["Section A"]):  # <<
    with ui.accordion_panel("Section A"):
        "Contents for Section A"
    with ui.accordion_panel("Section B"):
        "Contents for Section B"
    with ui.accordion_panel("Section C"):
        "Contents for Section C"


@render.code
def selected():
    return f"Open panel(s): {input.acc()}"
