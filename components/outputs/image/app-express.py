from pathlib import Path

from shiny.express import input, render, ui

here = Path(__file__).parent

ui.input_checkbox("show", "Show image?", value=True)


@render.image  # <<
def image():
    img = {"src": here / "shiny.png", "width": "100px"}  # <<
    return img if input.show() else None
