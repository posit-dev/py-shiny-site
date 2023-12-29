import faicons
from shiny import App, Inputs, Outputs, Session, render, ui

app_ui = ui.page_fluid(
    ui.input_slider("n", "Number of Billions", 1, 100, 20),  #<<
    ui.value_box(
        title="KPI Title",
        showcase=faicons.icon_svg('piggy-bank', width="50px"),
        value=ui.output_text("billions"),  #<<
        theme="bg-gradient-indigo-purple",
        full_screen=True,
    ),
)

def server(input, output, session):
    @render.text  #<<
    def billions():  #<<
        return f"${input.n()} Billion Dollars"  #<<

app = App(app_ui, server)
