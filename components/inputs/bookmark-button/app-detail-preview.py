from shiny import ui, render, App

app_ui = ui.page_fluid(
    ui.h4("Bookmark Demo"),
    ui.p("Change the inputs below, then click 'Bookmark' to save the state in the URL."),
    ui.input_text("name", "Name:", "Alice"),
    ui.input_slider("age", "Age:", 1, 100, 25),
    ui.input_bookmark_button(label="Bookmark this state"),
    ui.output_text_verbatim("state"),
)

def server(input, output, session):
    @render.text
    def state():
        return f"Name: {input.name()}\nAge: {input.age()}"

app = App(app_ui, server)
