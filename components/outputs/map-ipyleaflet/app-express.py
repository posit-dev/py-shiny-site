from ipyleaflet import Map  # <<
from shiny.express import ui
from shinywidgets import render_widget  # <<

ui.h2("An ipyleaflet Map")


@render_widget  # <<
def map():
    return Map(center=(50.6252978589571, 0.34580993652344), zoom=3)  # <<
