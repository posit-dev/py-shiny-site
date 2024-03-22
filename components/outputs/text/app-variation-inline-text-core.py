from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.input_text("Text", "Enter text", "Hello Shiny"),
    "You entered: ",
    ui.output_text("text", inline=True),  # <<
)


def server(input, output, session):
    @render.text
    def text():
        return input.Text()


app = App(app_ui, server)
