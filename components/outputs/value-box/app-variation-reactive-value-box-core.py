import faicons
from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.layout_columns(
        ui.h2("Spend Jeff's 2023 Earnings"),
        ui.input_slider("pct", "Percent of $70 Billion to donate", 0, 100, 20),  # <<
        ui.value_box(
            title="Save",
            showcase=faicons.icon_svg("piggy-bank", width="50px"),
            value=ui.output_ui("save"),  # <<
            theme="bg-gradient-orange-red",
        ),
        ui.value_box(
            title="Donate",
            showcase=faicons.icon_svg("hand-holding-dollar", width="50px"),
            value=ui.output_ui("donate"),  # <<
            theme="bg-gradient-blue-purple",
        ),
    ),
)


def server(input, output, session):
    @render.text  # <<
    def save():  # <<
        return f"${(1 - input.pct() / 100) * 70:.1f} Billion"  # <<

    @render.text  # <<
    def donate():  # <<
        return f"${input.pct() / 100 * 70:.1f} Billion"  # <<


app = App(app_ui, server)
