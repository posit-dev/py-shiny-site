from faicons import icon_svg
from shiny.express import input, render, ui

with ui.accordion(
    id="acc",
    open=["intro", "results"],
    multiple=True,
    class_="my-3",
    width="100%",
    height="500px",
):
    with ui.accordion_panel("Introduction", value="intro", icon=icon_svg("book")):
        "This panel is open by default and shows a leading icon."

    with ui.accordion_panel("Configuration", value="config", icon=icon_svg("gear")):
        ui.input_slider("n", "Value", 0, 100, 50)

    with ui.accordion_panel(
        "Results", value="results", icon=icon_svg("chart-simple")
    ):

        @render.text
        def result():
            return f"n = {input.n()}"


@render.text
def open_panels():
    return f"Open panel(s): {input.acc()}"
