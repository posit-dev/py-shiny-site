# FIXME: Rewrite as an Express app
from shiny import App, ui

app_ui = ui.page_fluid(
    ui.layout_column_wrap(
        ui.value_box( #<<
            "KPI Title",
            "$1 Billion Dollars",
            "Up 30% VS PREVIOUS 30 DAYS",
            theme="bg-gradient-indigo-purple",
            full_screen=True,
        ),
    )
)

app = App(app_ui, server=None)
