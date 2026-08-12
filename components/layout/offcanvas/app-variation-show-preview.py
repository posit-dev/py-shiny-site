from shiny import App, Inputs, Outputs, Session, reactive, ui

app_ui = ui.page_fluid(
    ui.input_action_button("show", "Show panel"),
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.effect
    @reactive.event(input.show)
    def _():
        ui.show_offcanvas(
            ui.offcanvas(
                ui.p("This panel was created by the server, not the UI."),
                title="Server panel",
                placement="left",
                id="server_panel",
            )
        )


app = App(app_ui, server=server)
