import faicons
from shiny.express import ui

with ui.layout_column_wrap():
    with ui.value_box(
        showcase=faicons.icon_svg("piggy-bank", width="50px"),
        theme="bg-gradient-indigo-purple",  # <<
        full_screen=True,
    ):
        "KPI Title"
        "$1 Billion Dollars"
        "Up 30% VS PREVIOUS 30 DAYS"

    with ui.value_box(
        showcase=faicons.icon_svg("piggy-bank", width="50px"),
        theme="text-green",  # <<
        showcase_layout="top right",  # <<
        full_screen=True,
    ):
        "KPI Title"
        "$1 Billion Dollars"
        "Up 30% VS PREVIOUS 30 DAYS"

    with ui.value_box(
        showcase=faicons.icon_svg("piggy-bank", width="50px"),
        theme="danger",  # <<
        showcase_layout="bottom",  # <<
        full_screen=True,
    ):
        "KPI Title"
        "$1 Billion Dollars"
        "Up 30% VS PREVIOUS 30 DAYS"
