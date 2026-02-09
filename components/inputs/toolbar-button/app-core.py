from faicons import icon_svg
from shiny import App, render, ui

app_ui = ui.page_fixed(
    ui.card(
        ui.card_header(
            "Document Actions",
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
            ui.output_text("save_status"),
        ),
        full_screen=True,
    )
)


def server(input, output, session):
    @render.text
    def save_status():
        return f"Save button clicked {input.save()} times"


app = App(app_ui, server)
