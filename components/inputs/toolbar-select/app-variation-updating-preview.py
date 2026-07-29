from faicons import icon_svg
from shiny import App, reactive, render, ui

app_ui = ui.page_fluid(
    ui.card(
        ui.card_header(
            "Data Dashboard",
            ui.toolbar(
                ui.toolbar_input_select(
                    id="view_mode",
                    label="View Mode",
                    choices=["Table", "Chart", "Map"],
                    icon=icon_svg("eye"),
                ),
                align="right",
            ),
        ),
        ui.card_body(
            ui.input_action_button("add_option", "Add 'Grid' Option"),
            ui.input_action_button("change_selection", "Select Chart"),
            ui.input_action_button("toggle_label", "Toggle Show Label"),
            ui.output_text("selected_view"),
        ),
        full_screen=True,
    ),
    {"class": "vh-100 d-flex justify-content-center align-items-center px-4"},
)


def server(input, output, session):
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

    @reactive.effect
    @reactive.event(input.toggle_label)
    def _():
        # Toggle show_label to display both icon and label
        current_click = input.toggle_label()
        ui.update_toolbar_input_select(
            "view_mode",
            show_label=current_click % 2 == 1,
        )

    @render.text
    def selected_view():
        return f"Currently viewing: {input.view_mode()}"


app = App(app_ui, server)
