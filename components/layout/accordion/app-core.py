from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.accordion(  # <<
        ui.accordion_panel("Section A", "Some narrative for section A"),
        ui.accordion_panel("Section B", "Some narrative for section B"),
        ui.accordion_panel("Section C", "Some narrative for section C"),
        id="acc",
        open=["Section A"],
    ),
    ui.output_code("selected"),
)


def server(input, output, session):
    @render.code
    def selected():
        return f"Open panel(s): {input.acc()}"


app = App(app_ui, server)
