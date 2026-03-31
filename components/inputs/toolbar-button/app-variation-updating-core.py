from faicons import icon_svg
from shiny import App, reactive, render, ui

app_ui = ui.page_fixed(
    ui.card(
        ui.card_header(
            "Document Editor",
            ui.toolbar(
                ui.toolbar_input_button(
                    id="save",
                    label="Save",
                    icon=icon_svg("floppy-disk"),
                ),
                align="right",
            ),
        ),
        ui.card_body(
            ui.input_action_button("toggle_disabled", "Toggle Save Button State"),
            ui.input_action_button("toggle_icon", "Toggle Icon"),
            ui.output_text("status"),
        ),
        full_screen=True,
    )
)


def server(input, output, session):
    @reactive.effect
    @reactive.event(input.toggle_disabled)
    def _():
        # Toggle between enabled and disabled
        current_click = input.toggle_disabled()
        is_disabled = current_click % 2 == 1
        ui.update_toolbar_input_button(
            "save",
            disabled=is_disabled,
            label="Save (Disabled)" if is_disabled else "Save",
        )

    @reactive.effect
    @reactive.event(input.toggle_icon)
    def _():
        # Toggle between two different icons
        current_click = input.toggle_icon()
        if current_click % 2 == 1:
            ui.update_toolbar_input_button(
                "save",
                icon=icon_svg("download"),
                label="Download",
            )
        else:
            ui.update_toolbar_input_button(
                "save",
                icon=icon_svg("floppy-disk"),
                label="Save",
            )

    @render.text
    def status():
        return f"Save button clicked {input.save()} times"


app = App(app_ui, server)
