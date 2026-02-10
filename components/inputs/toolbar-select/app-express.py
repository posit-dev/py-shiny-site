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
                show_label=True,
            )
            ui.toolbar_input_select(
                id="filter",
                label="Filter",
                choices=["All", "Active", "Archived"],
                icon=icon_svg("filter"),
            )

    @render.text
    def selected_view():
        return f"View Mode: {input.view_mode()}, Filter: {input.filter()}"
