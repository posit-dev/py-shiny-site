# FIXME: Rewrite as an Express app
import faicons
from shiny import App, ui
app_ui = ui.page_fluid(
ui.layout_column_wrap(
    ui.value_box(S
        "KPI Title",
        "$1 Billion Dollars",
        "Up 30% VS PREVIOUS 30 DAYS",
        showcase=faicons.icon_svg('piggy-bank', width="50px"),
        theme="bg-gradient-indigo-purple",  #<<
        full_screen=True,
    ),
    ui.value_box(
        "KPI Title",
        "$1 Billion Dollars",
        "Up 30% VS PREVIOUS 30 DAYS",
        showcase=faicons.icon_svg('piggy-bank', width="50px"),
        theme="text-green",  #<<
        showcase_layout="top right",  #<<
        full_screen=True,
    ),
    ui.value_box(
        "KPI Title",
        "$1 Billion Dollars",
        "Up 30% VS PREVIOUS 30 DAYS",
        showcase=faicons.icon_svg('piggy-bank', width="50px"),
        theme="purple",  #<<
        showcase_layout="bottom",  #<<
        full_screen=True,
    ),
)
)
app = App(app_ui, server=None)