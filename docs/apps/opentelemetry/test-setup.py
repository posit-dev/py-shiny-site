import os

import logfire

# Import Shiny and set collection level
from shiny import App, render, ui

# Optional: Configure Logfire if you haven't already (prompts for auth on first run)
logfire.configure()

os.environ["SHINY_OTEL_COLLECT"] = "reactivity"

# Use Shiny normally - tracing happens automatically
app_ui = ui.page_fluid(ui.input_slider("n", "N", 1, 100, 50), ui.output_text("result"))


def server(input, output, session):
    @render.text
    def result():
        return f"You selected: {input.n()}"


app = App(app_ui, server)
