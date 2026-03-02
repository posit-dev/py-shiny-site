from datetime import date
from shiny import ui, render, App

app_ui = ui.page_fluid(
    ui.download_link("download_data", "Download CSV"), # <<
)

def server(input, output, session):
    @render.download(filename=f"data-{date.today()}.csv")
    def download_data():
        yield "name,value\n"
        yield "Alice,100\n"
        yield "Bob,200\n"

app = App(app_ui, server)
