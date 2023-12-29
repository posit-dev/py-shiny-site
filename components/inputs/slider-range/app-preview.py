from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.input_slider("range", label="", value=[25, 70], min=1, max=100),
      {"class": "vh-100 d-flex justify-content-center align-items-center px-4"}
)
def server(input, output, session):
    @render.plot
    def hist():
        print(input.range())

app = App(app_ui, server)
