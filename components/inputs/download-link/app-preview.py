from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.download_link("download_data", "Download"),
    {"class": "vh-100 d-flex justify-content-center align-items-center px-4"},
)


def server(input, output, session):
    @render.download(filename="data.csv")
    def download_data():
        yield "name,value\n"
        yield "Alice,100\n"
        yield "Bob,200\n"


app = App(app_ui, server)
