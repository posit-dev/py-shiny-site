from faicons import icon_svg
from shiny import App, ui

app_ui = ui.page_fluid(
    ui.card(
        ui.card_header(
            "Data Analysis Report",
            ui.toolbar(
                ui.toolbar_input_button(
                    id="refresh",
                    label="Refresh",
                    icon=icon_svg("arrows-rotate"),
                ),
                ui.toolbar_input_button(
                    id="settings",
                    label="Settings",
                    icon=icon_svg("gear"),
                ),
                align="right",
            ),
            class_="bg-dark text-white"
        ),
        ui.card_body(
            ui.p("Analysis of Q4 sales data shows a 23% increase in revenue compared to Q3."),
            ui.p("Customer acquisition costs decreased by 15%, while retention rates improved by 8%."),
        ),
        ui.card_footer(
            ui.toolbar(
                ui.toolbar_input_button(
                    id="download",
                    label="Download Data",
                    icon=icon_svg("download"),
                ),
                ui.toolbar_spacer(),
                ui.toolbar_input_button(
                    id="export",
                    label="Export",
                    icon=icon_svg("file-export"),
                ),
                ui.toolbar_input_button(
                    id="share",
                    label="Share",
                    show_label=True,
                    icon=icon_svg("share-nodes"),
                ),
            ),
        )
    )
)


def server(input, output, session):
    pass


app = App(app_ui, server)
