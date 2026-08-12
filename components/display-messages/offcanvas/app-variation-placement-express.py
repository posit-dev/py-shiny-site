from shiny.express import ui

ui.offcanvas(
    ui.p("This panel slides in from the left."),
    title="Left",
    placement="left",  # <<
    width=300,  # <<
    trigger=ui.input_action_button("open_left", "From the left"),
    id="left_panel",
)

ui.offcanvas(
    ui.p("This panel slides in from the top."),
    title="Top",
    placement="top",  # <<
    height=200,  # <<
    trigger=ui.input_action_button("open_top", "From the top"),
    id="top_panel",
)

ui.offcanvas(
    ui.p("This panel slides in from the bottom."),
    title="Bottom",
    placement="bottom",  # <<
    trigger=ui.input_action_button("open_bottom", "From the bottom"),
    id="bottom_panel",
)
