from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.popover(
        ui.input_action_button("settings", "Settings", class_="mt-3"),
        ui.input_slider("n", "Number of points", 1, 100, 50),
        ui.input_select("color", "Color", ["red", "green", "blue"]),
        title="Plot settings",
        id="settings_popover",
    ),
    ui.output_code("summary"),
)


def server(input, output, session):
    @render.code
    def summary():
        return f"{input.n()} points in {input.color()}"


app = App(app_ui, server)
