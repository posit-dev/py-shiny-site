from faicons import icon_svg
from shiny import App, render, ui

app_ui = ui.page_fixed(
    ui.card(
        ui.card_header(
            "Data View",
            ui.toolbar(
                ui.toolbar_input_select(
                    id="view_mode",
                    label="View Mode",
                    choices=["Table", "Chart", "Map"],
                    icon=icon_svg("eye"),
                    show_label=True,
                ),
                ui.toolbar_input_select(
                    id="filter",
                    label="Filter",
                    choices=["All", "Active", "Archived"],
                    icon=icon_svg("filter"),
                ),
                align="right",
            ),
        ),
        ui.card_body(
            ui.output_text("selected_view"),
        ),
        full_screen=True,
    )
)


def server(input, output, session):
    @render.text
    def selected_view():
        return f"View Mode: {input.view_mode()}, Filter: {input.filter()}"


app = App(app_ui, server)
