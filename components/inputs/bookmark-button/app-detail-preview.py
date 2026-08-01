from starlette.requests import Request

from shiny import App, ui


def app_ui(request: Request):
    return ui.page_fluid(
        ui.row(
            ui.column(
                12,
                ui.input_radio_buttons(
                    "letter", "Choose a letter", choices=["A", "B", "C"], inline=True
                ),
                ui.input_bookmark_button(),
            ),
            {"class": "vh-100 justify-content-center align-items-center px-5"},
        ).add_class("text-center")
    )


def server(input, output, session):
    pass


app = App(app_ui, server, bookmark_store="url")
