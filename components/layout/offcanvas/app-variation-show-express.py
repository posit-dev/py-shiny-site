from shiny import reactive
from shiny.express import input, ui

ui.input_action_button("show", "Show panel")


@reactive.effect
@reactive.event(input.show)
def show_server_panel():
    ui.show_offcanvas(  # <<
        ui.offcanvas(
            ui.p("This panel was created by the server, not the UI."),
            title="Server panel",
            placement="left",
            id="server_panel",
        )
    )
