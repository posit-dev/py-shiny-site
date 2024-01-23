from shiny.express import ui

with ui.row():
    with ui.column(12):
        with ui.card("Width 12"):
            with ui.row():
                with ui.column(6):
                    with ui.card("Width 6"):
                        with ui.row():
                            with ui.column(6):
                                ui.card("Width 6")
                            with ui.column(6):
                                ui.card("Width 6")
                with ui.column(6):
                    ui.card("Width 6")
