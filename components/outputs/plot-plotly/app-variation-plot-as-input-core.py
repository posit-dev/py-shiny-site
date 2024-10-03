import plotly.express as px
import plotly.graph_objects as go
from plotly.callbacks import Points
import plotly.express as px
from palmerpenguins import load_penguins
from shiny import App, ui, render, reactive
from shinywidgets import output_widget, render_widget  

penguins = load_penguins()

app_ui = ui.page_fluid(
    output_widget("plot"),  
    "Click info",
    ui.output_text_verbatim("click_info", placeholder=True),
    "Hover info",
    ui.output_text_verbatim("hover_info", placeholder=True),   
    "Selection info (use box or lasso select)",
    ui.output_text_verbatim("selection_info", placeholder=True)
)


def server(input, output, session):

    click_reactive = reactive.value() # <<
    hover_reactive = reactive.value() # <<
    selection_reactive = reactive.value() # <<
    
    @render_widget  # <<
    def plot():  # <<
        fig = px.scatter(
            data_frame=penguins, x="body_mass_g", y="bill_length_mm"
        ).update_layout(
            yaxis_title="Bill Length (mm)",
            xaxis_title="Body Mass (g)",
        )
        w = go.FigureWidget(fig.data, fig.layout) # <<
        w.data[0].on_click(on_point_click) # <<
        w.data[0].on_hover(on_point_hover) # <<
        w.data[0].on_selection(on_point_selection) # <<
        return w # <<

    
    def on_point_click(trace, points, state): # <<
        click_reactive.set(points) # <<

    def on_point_hover(trace, points, state): # <<
        hover_reactive.set(points) # <<

    def on_point_selection(trace, points, state): # <<
        selection_reactive.set(points) # <<

    @render.text
    def click_info():
        return click_reactive.get()

    @render.text
    def hover_info():
        return hover_reactive.get()

    @render.text
    def selection_info():
        return selection_reactive.get()


app = App(app_ui, server)
