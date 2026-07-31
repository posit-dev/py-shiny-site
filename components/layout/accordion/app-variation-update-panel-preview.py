from shiny import reactive
from shiny.express import input, ui

ui.input_switch("update_panel", "Update (and open) sections")

with ui.accordion(id="acc", multiple=True):
    for letter in "ABC":
        with ui.accordion_panel(f"Section {letter}", value=f"sec_{letter}"):
            f"Some narrative for section {letter}"


@reactive.effect
@reactive.event(input.update_panel)
def _():
    txt = " (updated)" if input.update_panel() else ""
    show = bool(input.update_panel() % 2 == 1)
    for letter in "ABC":
        ui.update_accordion_panel(
            "acc",
            f"sec_{letter}",
            f"Some{txt} narrative for section {letter}",
            title=f"Section {letter}{txt}",
            show=show,
        )
