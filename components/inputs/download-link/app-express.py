from datetime import date

from shiny.express import render, ui
from shiny.ui import download_link

download_link("download_data", "Download CSV")  # <<

# `@render.download` auto-places a download *button*; wrap it in `ui.hold()`
# to register the handler without the button, and pair it with the
# `download_link()` above via the matching id/function name.
with ui.hold():

    @render.download(filename=lambda: f"data-{date.today().isoformat()}.csv")
    def download_data():
        yield "name,value\n"
        yield "Alice,100\n"
        yield "Bob,200\n"
