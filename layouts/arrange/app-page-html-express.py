from pathlib import Path

from shiny.express import input, render, ui

ui.page_opts(html=Path(__file__).parent / "custom-page.html")  # <<


@render.text
def greeting():
    return f"Hello, {input.name()}!"
