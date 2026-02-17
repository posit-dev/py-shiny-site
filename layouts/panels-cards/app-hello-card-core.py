from shiny import App, ui

app_ui = ui.page_fluid(
    ui.card(
        ui.card_header(
            "A header",
            class_="bg-dark"
        ),
        ui.card_body(
            ui.markdown("Some text with a [link](https://github.com)")
        )
    )
)


def server(input, output, session):
    pass


app = App(app_ui, server)
