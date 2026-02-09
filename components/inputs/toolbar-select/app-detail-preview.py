from faicons import icon_svg
from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.card(
        ui.card_header(
            "Data Dashboard",
            ui.toolbar(
                ui.toolbar_input_select(
                    id="time_range",
                    label="Time Range",
                    choices={
                        "7d": "Last 7 days",
                        "30d": "Last 30 days",
                        "90d": "Last 90 days",
                        "1y": "Last year",
                    },
                    selected="30d",
                    icon=icon_svg("calendar"),
                ),
                ui.toolbar_divider(),
                ui.toolbar_input_select(
                    id="view_type",
                    label="View Type",
                    choices=["Summary", "Detailed", "Comparison"],
                    icon=icon_svg("chart-line"),
                ),
                align="right",
            ),
        ),
        ui.card_body(
            ui.h4("Dashboard Settings"),
            ui.output_text_verbatim("settings"),
        ),
        full_screen=True,
        height="350px",
    )
)


def server(input, output, session):
    @render.text
    def settings():
        time_labels = {
            "7d": "Last 7 days",
            "30d": "Last 30 days",
            "90d": "Last 90 days",
            "1y": "Last year",
        }
        return f"Time Range: {time_labels.get(input.time_range(), input.time_range())}\nView Type: {input.view_type()}"


app = App(app_ui, server)
