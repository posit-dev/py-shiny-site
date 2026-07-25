from datetime import date

from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.h5("Download example data"),
    ui.download_link("download_data", "Download CSV"),
    ui.p("Click the link to download a CSV file generated in memory."),
)


def server(input, output, session):
    @render.download(filename=lambda: f"data-{date.today().isoformat()}.csv")
    def download_data():
        yield "name,value\n"
        yield "Alice,100\n"
        yield "Bob,200\n"


app = App(app_ui, server)
