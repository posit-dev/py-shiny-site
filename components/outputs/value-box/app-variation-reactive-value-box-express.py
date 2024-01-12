import faicons
from shiny import render
from shiny.express import input, ui

with ui.layout_columns():
    ui.h2("Spend Jeff's 2023 Earnings")
    ui.input_slider("pct", "Percent of $70 Billion to donate", 0, 100, 20)  # <<

    with ui.value_box(
        showcase=faicons.icon_svg("piggy-bank", width="50px"),
        theme="bg-gradient-orange-red",
    ):
        "Save"

        @render.ui  # <<
        def save():  # <<
            return f"${(1 - input.pct() / 100) * 70:.1f} Billion"  # <<

    with ui.value_box(
        showcase=faicons.icon_svg("hand-holding-dollar", width="50px"),
        theme="bg-gradient-blue-purple",
    ):
        "Donate"

        @render.ui  # <<
        def donate():  # <<
            return f"${input.pct() / 100 * 70:.1f} Billion"  # <<
