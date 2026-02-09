from faicons import icon_svg
from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.card(
        ui.card_header(
            "Advanced Toolbar",
            ui.toolbar(
                ui.toolbar_input_button(
                    id="new",
                    label="New",
                    icon=icon_svg("plus"),
                ),
                ui.toolbar_input_button(
                    id="save",
                    label="Save",
                    icon=icon_svg("floppy-disk"),
                ),
                ui.toolbar_spacer(),
                ui.toolbar_input_select(
                    id="view",
                    label="View",
                    choices=["Grid", "List", "Timeline"],
                    icon=icon_svg("eye"),
                ),
                ui.toolbar_divider(),
                ui.toolbar_input_button(
                    id="settings",
                    label="Settings",
                    icon=icon_svg("gear"),
                ),
                align="right",
                width="100%",
            ),
        ),
        ui.card_body(
            ui.h4("Toolbar Interactions"),
            ui.output_text_verbatim("toolbar_info"),
        ),
        full_screen=True,
        height="350px",
    )
)


def server(input, output, session):
    @render.text
    def toolbar_info():
        return f"""New: {input.new()} clicks
Save: {input.save()} clicks
Settings: {input.settings()} clicks
View: {input.view()}"""


app = App(app_ui, server)
