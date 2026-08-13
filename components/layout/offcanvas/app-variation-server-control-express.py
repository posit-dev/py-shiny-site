from shiny import reactive
from shiny.express import input, render, ui

ui.offcanvas(
    ui.p("This panel has no trigger of its own; the server opens and closes it."),
    ui.input_action_button("hide", "Hide"),  # <<
    title="Server controlled",
    id="panel",  # <<
)

ui.input_action_button("show", "Show")
ui.input_action_button("toggle", "Toggle")


@render.code
def state():
    return f"Panel is {'open' if input.panel() else 'closed'}"


@reactive.effect
@reactive.event(input.show)
def show_panel():
    ui.toggle_offcanvas("panel", show=True)  # <<


@reactive.effect
@reactive.event(input.hide)
def hide_panel():
    ui.hide_offcanvas("panel")  # <<


@reactive.effect
@reactive.event(input.toggle)
def toggle_panel():
    ui.toggle_offcanvas("panel")  # <<
