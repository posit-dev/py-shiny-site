from faicons import icon_svg
from shiny import reactive
from shiny.express import input, ui

with ui.card(full_screen=True):
    with ui.card_header():
        "Data Dashboard"
        with ui.toolbar(align="right"):
            ui.toolbar_input_select(
                id="view_mode",
                label="View Mode",
                choices=["Table", "Chart", "Map"],
                icon=icon_svg("eye"),
            )

    with ui.card_body():
        ui.input_action_button("add_option", "Add 'Grid' Option")
        ui.input_action_button("change_selection", "Select Chart")

        ui.output_text("selected_view")


@reactive.effect
@reactive.event(input.add_option)
def _():
    # Add a new choice to the select
    ui.update_toolbar_input_select(
        "view_mode",
        choices=["Table", "Chart", "Map", "Grid"],
        label="View Mode (Updated)",
    )


@reactive.effect
@reactive.event(input.change_selection)
def _():
    # Change the selected value
    ui.update_toolbar_input_select(
        "view_mode",
        selected="Chart",
    )


@ui.render.text
def selected_view():
    return f"Currently viewing: {input.view_mode()}"
