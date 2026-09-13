from pathlib import Path

from shiny import App, render, ui

app_ui = ui.page_html(Path(__file__).parent / "custom-page.html")  # <<


def server(input, output, session):
    @render.text
    def greeting():
        return f"Hello, {input.name()}!"


app = App(app_ui, server)
