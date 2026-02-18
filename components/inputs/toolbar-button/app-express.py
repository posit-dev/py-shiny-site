from faicons import icon_svg
from shiny.express import input, render, ui

with ui.card(full_screen=True):
    with ui.card_header():
        "Document Actions"
        with ui.toolbar(align="right"):
            ui.toolbar_input_button(
                id="label_only",
                label="Label Only",
            )
            ui.toolbar_input_button(
                id="icon_and_label",
                label="Icon + Label",
                icon=icon_svg("download"),
                show_label=True,
            )
            ui.toolbar_input_button(
                id="icon_only",
                label="Icon Only",
                icon=icon_svg("floppy-disk"),
            )

    @render.text
    def button_status():
        return f"Buttons clicked - Label: {input.label_only()}, Icon: {input.icon_only()}, Both: {input.icon_and_label()}"
