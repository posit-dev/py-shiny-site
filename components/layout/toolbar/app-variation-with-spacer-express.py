from faicons import icon_svg
from shiny.express import ui

with ui.card(full_screen=True):
    with ui.card_header():
        "Split Toolbar"
        with ui.toolbar(align="left", width="100%"):
            ui.toolbar_input_button(
                id="back",
                label="Back",
                icon=icon_svg("arrow-left"),
            )
            ui.toolbar_spacer()
            ui.toolbar_input_button(
                id="help",
                label="Help",
                icon=icon_svg("arrow-right"),
            )

    ui.p("Toolbar spacer pushes buttons to opposite ends.")
