from shiny.express import input, render, ui

ui.offcanvas(  # <<
    ui.p("An offcanvas panel slides in from the edge of the page."),
    ui.p("Close it with the button, the backdrop, or the Escape key."),
    title="Details",
    trigger=ui.input_action_button("open", "Open panel"),  # <<
    id="panel",  # <<
)


@render.code
def state():
    return f"Panel is {'open' if input.panel() else 'closed'}"  # <<
