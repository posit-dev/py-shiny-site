from shiny import ui, render, App

app_ui = ui.page_fluid(
    ui.input_text("name", "Name:", "Alice"),
    ui.input_slider("age", "Age:", 1, 100, 25),
    ui.input_bookmark_button(label="Bookmark"),
    ui.output_text_verbatim("url"),
    {"class": "vh-100 d-flex justify-content-center align-items-center px-4"},
)

def server(input, output, session):
    @render.text
    def url():
        return f"Bookmarkable URL will update when you bookmark"

app = App(app_ui, server)
