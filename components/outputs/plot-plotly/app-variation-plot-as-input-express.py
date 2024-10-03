import plotly.express as px
import plotly.graph_objects as go
from plotly.callbacks import Points
from shinywidgets import render_plotly
from palmerpenguins import load_penguins
from shiny import render, reactive
from shiny.express import input, ui
from shiny.ui import output_code, output_plot

penguins = load_penguins()


@render_plotly  # <<
def plot():  # <<
    fig = px.scatter(
        data_frame=penguins, x="body_mass_g", y="bill_length_mm"
    ).update_layout(
        yaxis_title="Bill Length (mm)",
        xaxis_title="Body Mass (g)",
    )
    # Need to create a FigureWidget() for on_click to work
    w = go.FigureWidget(fig.data, fig.layout) # <<
    w.data[0].on_click(on_point_click) # <<
    w.data[0].on_hover(on_point_hover) # <<
    w.data[0].on_selection(on_point_selection) # <<
    return w # <<


# Capture the clicked point in a reactive value
click_reactive = reactive.value() # <<
hover_reactive = reactive.value() # <<
selection_reactive = reactive.value() # <<

def on_point_click(trace, points, state): # <<
    click_reactive.set(points) # <<

def on_point_hover(trace, points, state): # <<
    hover_reactive.set(points) # <<

def on_point_selection(trace, points, state): # <<
    selection_reactive.set(points) # <<


"Click info"
@render.code
def click_info():
    return str(click_reactive.get())

"Hover info"
@render.code
def hover_info():
    return str(hover_reactive.get())

"Selection info (use box or lasso select)"
@render.code
def selection_info():
    return str(selection_reactive.get())
