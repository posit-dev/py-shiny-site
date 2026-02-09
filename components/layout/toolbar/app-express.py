from faicons import icon_svg
from shiny.express import input, render, ui

with ui.card(full_screen=True):
    with ui.card_header():
        "Toolbar Example"
        with ui.toolbar(align="right"):
            ui.toolbar_input_button(
                id="action1",
                label="Action",
                icon=icon_svg("bolt"),
            )
            ui.toolbar_divider()
            ui.toolbar_input_select(
                id="options",
                label="Options",
                choices=["Option 1", "Option 2", "Option 3"],
                icon=icon_svg("sliders"),
            )

    @render.text
    def toolbar_status():
        return f"Button clicks: {input.action1()}, Selected: {input.options()}"
