from faicons import icon_svg
from shiny.express import input, render, ui

with ui.card(full_screen=True):
    with ui.card_header():
        "Document Actions"
        with ui.toolbar(align="right"):
            ui.toolbar_input_button(
                id="save",
                label="Save",
                icon=icon_svg("floppy-disk"),
            )

    @render.text
    def save_status():
        return f"Save button clicked {input.save()} times"
