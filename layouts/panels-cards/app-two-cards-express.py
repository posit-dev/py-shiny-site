from shiny.express import input, render, ui

with ui.layout_column_wrap(width=1/2, height="300px"):
    with ui.card(full_screen=True):
        ui.card_header("User Settings")
        with ui.card_body():
            ui.input_text("name", "Name", "John Doe")
            ui.input_slider("age", "Age", 18, 100, 30)
            ui.input_select("role", "Role", choices=["Admin", "User", "Guest"])
        with ui.card_footer():
            ui.input_action_button("save", "Save Changes", class_="btn-primary")

    with ui.card(full_screen=True):
        ui.card_header("Activity Summary")
        with ui.card_body():
            @render.text
            def summary():
                return f"Hello, {input.name()}!"

            ui.tags.ul(
                ui.tags.li("Last login: 2 hours ago"),
                ui.tags.li("Messages: 12 unread"),
                ui.tags.li("Tasks: 5 pending"),
            )
