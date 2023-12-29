# FIXME: Rewrite as an Express app
from ipyleaflet import GeoJSON, Map  #<<
from shiny import App, ui
from shinywidgets import output_widget, render_widget  #<<

app_ui = ui.page_fluid(output_widget("my_map"))  #<<

def server(input, output, session):

    @render_widget  #<<
    def my_map():  
        return Map(center=(50.6252978589571, 0.34580993652344), zoom=3)  #<<

app = App(app_ui, server)
