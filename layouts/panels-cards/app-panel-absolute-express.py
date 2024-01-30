from functools import partial

from htmltools import css
from shiny.express import ui
from shiny.ui import page_fillable

page_style = css(
    background_image="url(https://unsplash.com/photos/XKXGghL7GQc/download?force=true&w=1920)",
    background_repeat="no-repeat",
    background_size="cover",
    background_position="center bottom",
)

ui.page_opts(page_fn=partial(page_fillable, style=page_style))

with ui.panel_absolute(  # <<
    width="300px",  # <<
    right="50px",  # <<
    top="50px",  # <<
    draggable=True,  # <<
):  # <<
    with ui.panel_well():
        ui.h2("Draggable panel")
        "Move this panel anywhere you want."
