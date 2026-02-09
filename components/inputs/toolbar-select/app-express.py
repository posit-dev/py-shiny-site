from faicons import icon_svg
from shiny.express import input, render, ui

with ui.card(full_screen=True):
    with ui.card_header():
        "Data View"
        with ui.toolbar(align="right"):
            ui.toolbar_input_select(
                id="view_mode",
                label="View Mode",
                choices=["Table", "Chart", "Map"],
                icon=icon_svg("eye"),
            )

    @render.text
    def selected_view():
        return f"Currently viewing: {input.view_mode()}"
