from faicons import icon_svg
from shiny.express import input, ui

with ui.card():
    with ui.card_header(class_="bg-dark text-white"):
        "Data Analysis Report"
        with ui.toolbar(align="right"):
            ui.toolbar_input_button(
                id="refresh",
                label="Refresh",
                icon=icon_svg("arrows-rotate"),
            )
            ui.toolbar_input_button(
                id="settings",
                label="Settings",
                icon=icon_svg("gear"),
            )

    ui.p("Analysis of Q4 sales data shows a 23% increase in revenue compared to Q3.")
    ui.p("Customer acquisition costs decreased by 15%, while retention rates improved by 8%.")

    with ui.card_footer():
        with ui.toolbar():
            ui.toolbar_input_button(
                id="export",
                label="Export",
                icon=icon_svg("file-export"),
            )
            ui.toolbar_input_button(
                id="share",
                label="Share",
                icon=icon_svg("share-nodes"),
            )
            ui.toolbar_spacer()
            ui.toolbar_input_button(
                id="save",
                label="Save",
                icon=icon_svg("floppy-disk"),
            )
