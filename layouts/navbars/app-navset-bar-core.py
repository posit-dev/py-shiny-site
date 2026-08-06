from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.h4("Quarterly report"),
    "This heading and text are outside the navbar.",
    ui.navset_bar(  # <<
        ui.nav_panel("Summary", "Summary content"),  # <<
        ui.nav_panel("Details", "Details content"),  # <<
        ui.nav_spacer(),  # <<
        ui.nav_panel("About", "About content"),  # <<
        title="Sections",  # <<
        id="section",  # <<
    ),  # <<
    ui.h6("Selected section:"),
    ui.output_code("selected"),
)


def server(input, output, session):
    @render.code
    def selected():
        return input.section()


app = App(app_ui, server)
