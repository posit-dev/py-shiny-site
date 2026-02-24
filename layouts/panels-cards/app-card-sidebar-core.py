from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.card(
        ui.card_header("Data Explorer"),
        ui.layout_sidebar(
            ui.sidebar(
                ui.input_select("dataset", "Dataset", ["mtcars", "iris", "airquality"]),
                ui.input_slider("rows", "Rows to show", 1, 10, 5),
                ui.input_action_button("refresh", "Refresh"),
            ),
            ui.card_body(
                ui.output_text("info"),
                ui.p("Data preview would appear here..."),
            ),
        ),
        full_screen=True,
        height="350px",
    )
)


def server(input, output, session):
    @render.text
    def info():
        return f"Showing {input.rows()} rows from {input.dataset()}"


app = App(app_ui, server)
