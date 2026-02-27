from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.layout_column_wrap(
        ui.card(
            ui.card_header("User Settings"),
            ui.card_body(
                ui.input_text("name", "Name", "John Doe"),
                ui.input_slider("age", "Age", 18, 100, 30),
            ),
            ui.card_footer(
                ui.input_action_button("save", "Save Changes", class_="btn-primary")
            ),
            full_screen=True,
        ),
        ui.card(
            ui.card_header("Activity Summary"),
            ui.card_body(
                ui.output_text("summary"),
                ui.tags.ul(
                    ui.tags.li("Last login: 2 hours ago"),
                    ui.tags.li("Messages: 12 unread"),
                    ui.tags.li("Tasks: 5 pending"),
                ),
            ),
            full_screen=True,
        ),
        width=1/2,
        height="300px",
    )
)


def server(input, output, session):
    @render.text
    def summary():
        return f"Hello, {input.name()}!"


app = App(app_ui, server)
