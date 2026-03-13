from shiny import ui, render, App

app_ui = ui.page_fluid(
    ui.download_button("download", "Download"),
    {"class": "vh-100 d-flex justify-content-center align-items-center px-4"},
)

def server(input, output, session):
    @render.download(filename="data.csv")
    def download():
        yield "a,b,c\n1,2,3\n4,5,6"

app = App(app_ui, server)
