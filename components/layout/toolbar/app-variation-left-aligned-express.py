from faicons import icon_svg
from shiny.express import ui

with ui.card(full_screen=True):
    with ui.card_header():
        "Left-Aligned Toolbar"
        with ui.toolbar(align="left"):
            ui.toolbar_input_button(
                id="undo",
                label="Undo",
                icon=icon_svg("rotate-left"),
            )
            ui.toolbar_input_button(
                id="redo",
                label="Redo",
                icon=icon_svg("rotate-right"),
            )

    ui.p("Toolbar aligned to the left side of the header.")
