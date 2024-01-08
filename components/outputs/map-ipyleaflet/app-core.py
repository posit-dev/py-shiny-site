from ipyleaflet import GeoJSON, Map  #<<
from shiny import App, ui
from shinywidgets import output_widget, register_widget  #<<

app_ui = ui.page_fluid(output_widget("map"))  #<<

def server(input, output, session):
    my_map = Map(center=(50.6252978589571, 0.34580993652344), zoom=3)  #<<
    register_widget("map", my_map)  #<<

app = App(app_ui, server)
