## file: app.py
from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.accordion(
        ui.accordion_panel(
            "Overview",
            "Accordions group content into vertically collapsing sections.",
        ),
        ui.accordion_panel(
            "Details",
            "Only the panels you choose start open; the rest stay collapsed.",
        ),
        ui.accordion_panel(
            "More",
            "Give the accordion an id to read which panels are open.",
        ),
        id="acc",
    ),
    ui.output_code("selected"),
    class_="px-3 pt-3",
)


def server(input, output, session):
    @render.code
    def selected():
        return f"Open panel(s): {input.acc()}"


app = App(app_ui, server)
