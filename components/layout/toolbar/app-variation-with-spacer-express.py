from faicons import icon_svg
from shiny.express import ui

with ui.card(full_screen=True):
    with ui.card_header():
        with ui.toolbar(align="left", width="100%"):
            ui.toolbar_input_button(
                id="left",
                label="Left",
                icon=icon_svg("arrow-left"),
            )
            ui.toolbar_input_button(
                id="right",
                label="Right",
                icon=icon_svg("arrow-right"),
            )
            ui.toolbar_input_button(
                id="refresh",
                label="Refresh",
                icon=icon_svg("arrows-rotate"),
            )
            ui.toolbar_spacer()
            ui.toolbar_input_button(
                id="export",
                label="Export",
                icon=icon_svg("download"),
            )
            ui.toolbar_input_button(
                id="save",
                label="Save",
                icon=icon_svg("floppy-disk"),
            )

    ui.p("Toolbar spacer pushes buttons to opposite ends.")
