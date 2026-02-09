from faicons import icon_svg
from shiny import App, render, ui

app_ui = ui.page_fixed(
    ui.card(
        ui.card_header(
            "Toolbar Example",
            ui.toolbar(
                ui.toolbar_input_button(
                    id="action1",
                    label="Action",
                    icon=icon_svg("bolt"),
                ),
                ui.toolbar_divider(),
                ui.toolbar_input_select(
                    id="options",
                    label="Options",
                    choices=["Option 1", "Option 2", "Option 3"],
                    icon=icon_svg("sliders"),
                ),
                align="right",
            ),
        ),
        ui.card_body(
            ui.output_text("toolbar_status"),
        ),
        full_screen=True,
    )
)


def server(input, output, session):
    @render.text
    def toolbar_status():
        return f"Button clicks: {input.action1()}, Selected: {input.options()}"


app = App(app_ui, server)
