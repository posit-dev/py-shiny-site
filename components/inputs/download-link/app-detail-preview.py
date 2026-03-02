from datetime import date
from shiny import ui, render, App

app_ui = ui.page_fluid(
    ui.h4("Download Example Data"),
    ui.download_link("download_data", "Download CSV File"),
    ui.p("Click the link to download a CSV file with sample data."),
)

def server(input, output, session):
    @render.download(filename=f"sample-data-{date.today()}.csv")
    def download_data():
        yield "name,age,city\n"
        yield "Alice,25,New York\n"
        yield "Bob,30,San Francisco\n"
        yield "Charlie,35,Chicago\n"

app = App(app_ui, server)
