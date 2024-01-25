from functools import partial

from shiny.express import ui
from shiny.ui import page_navbar

ui.page_opts(
    title="App with navbar",  # <<
    page_fn=partial(page_navbar, id="page", position="fixed-bottom"),  # <<
)

with ui.nav_panel("A"):  # <<
    "Page A content"

with ui.nav_panel("B"):  # <<
    "Page B content"

with ui.nav_panel("C"):  # <<
    "Page C content"
