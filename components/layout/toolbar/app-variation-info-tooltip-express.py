from faicons import icon_svg
from shiny.express import ui

with ui.card():
    ui.card_header("Data Settings")
    ui.input_slider(
        "threshold",
        label=ui.toolbar(
            ui.toolbar_input_button(
                "threshold_info",
                label="About this setting",
                icon=icon_svg("circle-info"),
                tooltip="Standard deviations from the mean before a value is flagged as an outlier.",
            ),
            "Outlier threshold",
            align="left",
        ),
        min=1,
        max=5,
        value=2,
        step=0.5,
    )
    ui.input_numeric(
        "sample_size",
        label=ui.toolbar(
            ui.toolbar_input_button(
                "sample_info",
                label="About this setting",
                icon=icon_svg("circle-info"),
                tooltip="Number of observations to draw from the dataset for each analysis run.",
            ),
            "Sample size",
            align="left",
        ),
        value=100,
        min=10,
        max=1000,
        step=10,
    )