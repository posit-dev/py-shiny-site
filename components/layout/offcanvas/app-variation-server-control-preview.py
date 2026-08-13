from shiny import App, Inputs, Outputs, Session, reactive, render, ui

app_ui = ui.page_fluid(
    ui.offcanvas(
        ui.p("This panel has no trigger of its own; the server opens and closes it."),
        ui.input_action_button("hide", "Hide"),
        title="Server controlled",
        id="panel",
    ),
    ui.input_action_button("show", "Show"),
    ui.input_action_button("toggle", "Toggle"),
    ui.output_code("state"),
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.effect
    @reactive.event(input.show)
    def _():
        ui.toggle_offcanvas("panel", show=True)

    @reactive.effect
    @reactive.event(input.hide)
    def _():
        ui.hide_offcanvas("panel")

    @reactive.effect
    @reactive.event(input.toggle)
    def _():
        ui.toggle_offcanvas("panel")

    @render.code
    def state():
        return f"Panel is {'open' if input.panel() else 'closed'}"


app = App(app_ui, server=server)
