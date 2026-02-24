from shiny.express import input, render, ui

with ui.card(full_screen=True, height="350px"):
    ui.card_header("Data Explorer")
    with ui.layout_sidebar():
        with ui.sidebar():
            ui.input_select("dataset", "Dataset", ["mtcars", "iris", "airquality"])
            ui.input_slider("rows", "Rows to show", 1, 10, 5)
            ui.input_action_button("refresh", "Refresh")
        with ui.card_body():
            @render.text
            def info():
                return f"Showing {input.rows()} rows from {input.dataset()}"

            ui.p("Data preview would appear here...")
