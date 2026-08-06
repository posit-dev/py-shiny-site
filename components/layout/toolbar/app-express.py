from faicons import icon_svg
from shiny.express import input, render, ui

with ui.card(full_screen=True):
    with ui.card_header():
        "Header"
        with ui.toolbar(align="right"):
            ui.toolbar_input_button(
                id="action1",
                label="Refresh",
                icon=icon_svg("arrows-rotate"),
            )
            ui.toolbar_divider()
            ui.toolbar_input_select(
                id="options",
                label="Filter",
                choices=["ABC", "CDE", "EFG"],
            )

    @render.text
    def toolbar_status():
        return f"Button clicks: {input.action1()}, Selected: {input.options()}"
