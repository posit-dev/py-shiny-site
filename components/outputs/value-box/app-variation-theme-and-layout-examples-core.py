import faicons
from shiny import App, ui

app_ui = ui.page_fluid(
    ui.layout_column_wrap(
        ui.value_box(
            "KPI Title",
            "$1 Billion Dollars",
            "Up 30% VS PREVIOUS 30 DAYS",
            showcase=faicons.icon_svg("piggy-bank", width="50px"),
            theme="bg-gradient-indigo-purple",  # <<
        ),
        ui.value_box(
            "KPI Title",
            "$1 Billion Dollars",
            "Up 30% VS PREVIOUS 30 DAYS",
            showcase=faicons.icon_svg("piggy-bank", width="50px"),
            theme="text-green",  # <<
            showcase_layout="top right",  # <<
        ),
        ui.value_box(
            "KPI Title",
            "$1 Billion Dollars",
            "Up 30% VS PREVIOUS 30 DAYS",
            showcase=faicons.icon_svg("piggy-bank", width="50px"),
            theme="danger",  # <<
            showcase_layout="bottom",  # <<
        ),
    )
)
app = App(app_ui, server=None)
