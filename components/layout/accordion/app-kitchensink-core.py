from faicons import icon_svg
from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.accordion(
        ui.accordion_panel(
            "Introduction",
            "This panel is open by default and shows a leading icon.",
            value="intro",
            icon=icon_svg("book"),
        ),
        ui.accordion_panel(
            "Configuration",
            ui.input_slider("n", "Value", 0, 100, 50),
            value="config",
            icon=icon_svg("gear"),
        ),
        ui.accordion_panel(
            "Results",
            ui.output_text_verbatim("result"),
            value="results",
            icon=icon_svg("chart-simple"),
        ),
        id="acc",
        open=["intro", "results"],
        multiple=True,
        class_="my-3",
        width="100%",
        height="500px",
    ),
    ui.output_text_verbatim("open_panels"),
)


def server(input, output, session):
    @render.text
    def result():
        return f"n = {input.n()}"

    @render.text
    def open_panels():
        return f"Open panel(s): {input.acc()}"


app = App(app_ui, server)
