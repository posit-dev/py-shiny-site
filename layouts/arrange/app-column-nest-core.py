from shiny import App, ui

app_ui = ui.page_fluid(
    ui.row(
        ui.column(
            12,
            ui.card(
                "Width 12",
                ui.row(
                    ui.column(
                        6,
                        ui.card(
                            "Width 6",
                            ui.row(
                                ui.column(6, ui.card("Width 6")),
                                ui.column(6, ui.card("Width 6")),
                            ),
                        ),
                    ),
                    ui.column(6, ui.card("Width 6")),
                ),
            ),
        )
    )
)


def server(input, output, session):
    return None


app = App(app_ui, server)
