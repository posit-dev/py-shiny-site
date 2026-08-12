from shiny import App, Inputs, Outputs, Session, render, ui

app_ui = ui.page_fluid(
    ui.offcanvas(
        ui.p("An offcanvas panel slides in from the edge of the page."),
        ui.p("Close it with the button, the backdrop, or the Escape key."),
        title="Details",
        trigger=ui.input_action_button("open", "Open panel"),
        id="panel",
    ),
    ui.output_code("state"),
)


def server(input: Inputs, output: Outputs, session: Session):
    @render.code
    def state():
        return f"Panel is {'open' if input.panel() else 'closed'}"


app = App(app_ui, server=server)
