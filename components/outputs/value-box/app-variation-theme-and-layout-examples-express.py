import faicons
from shiny.express import ui

with ui.layout_column_wrap():
    with ui.value_box(
        showcase=faicons.icon_svg("piggy-bank", width="50px"),
        theme="bg-gradient-indigo-purple",  # <<
    ):
        "KPI Title"
        "$1 Billion Dollars"
        "Up 30% VS PREVIOUS 30 DAYS"

    with ui.value_box(
        showcase=faicons.icon_svg("piggy-bank", width="50px"),
        theme="text-green",  # <<
        showcase_layout="top right",  # <<
    ):
        "KPI Title"
        "$1 Billion Dollars"
        "Up 30% VS PREVIOUS 30 DAYS"

    with ui.value_box(
        showcase=faicons.icon_svg("piggy-bank", width="50px"),
        theme="danger",  # <<
        showcase_layout="bottom",  # <<
    ):
        "KPI Title"
        "$1 Billion Dollars"
        "Up 30% VS PREVIOUS 30 DAYS"
