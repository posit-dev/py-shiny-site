from shiny import App, reactive, ui

app_ui = ui.page_fluid(
    ui.input_radio_buttons(
        "controller", "Show panel", ["1", "2", "3"], selected="1", inline=True
    ),
    ui.navset_hidden(  # <<
        ui.nav_panel(None, "Panel 1 content", value="panel1"),  # <<
        ui.nav_panel(None, "Panel 2 content", value="panel2"),  # <<
        ui.nav_panel(None, "Panel 3 content", value="panel3"),  # <<
        id="hidden_tabs",  # <<
    ),  # <<
)


def server(input, output, session):
    @reactive.effect
    @reactive.event(input.controller)
    def _():
        ui.update_navset("hidden_tabs", selected="panel" + input.controller())  # <<


app = App(app_ui, server)
