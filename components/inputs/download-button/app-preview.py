from shiny import ui, render, App

app_ui = ui.page_fluid(
    ui.download_button("download", "Download"),
)

def server(input, output, session):
    @render.download(filename="data.csv")
    def download():
        return "a,b,c\n1,2,3\n4,5,6"

app = App(app_ui, server)
