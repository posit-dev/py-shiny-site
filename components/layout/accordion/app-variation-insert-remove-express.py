from shiny import reactive
from shiny.express import input, ui

with ui.layout_columns():
    ui.input_action_button("add_panel", "Add panel")
    ui.input_action_button("remove_panel", "Remove last panel")

with ui.accordion(id="acc", multiple=True):
    with ui.accordion_panel("Section 1", value="sec_1"):
        "Some narrative for section 1"

count = reactive.value(1)


@reactive.effect
@reactive.event(input.add_panel)
def _():
    n = count() + 1
    count.set(n)
    ui.insert_accordion_panel(  # <<
        "acc",
        ui.accordion_panel(
            f"Section {n}", f"Some narrative for section {n}", value=f"sec_{n}"
        ),
    )


@reactive.effect
@reactive.event(input.remove_panel)
def _():
    n = count()
    if n > 0:
        ui.remove_accordion_panel("acc", f"sec_{n}")
        count.set(n - 1)
