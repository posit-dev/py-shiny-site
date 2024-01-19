from shiny.express import ui
from shiny.ui import page_navbar

ui.page_opts(
    title="App with navbar",  # <<
    page_fn=lambda *args, **kwargs: page_navbar(
        *args,
        id="page",  # <<
        **kwargs,
    ),  # <<
)

with ui.nav_panel("A"):  # <<
    "Page A content"

with ui.nav_panel("B"):  # <<
    "Page B content"

with ui.nav_panel("C"):  # <<
    "Page C content"
