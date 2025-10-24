import polars as pl
from setup import append_info, load_data, save_info
from shiny import reactive
from shiny.express import app_opts, input, render, ui

with ui.sidebar():
    ui.input_text("name_input", "Enter your name", placeholder="Your name here")
    ui.input_checkbox("checkbox", "I like checkboxes")
    ui.input_slider("slider", "My favorite number is:", min=0, max=100, value=50)
    ui.input_action_button("submit_button", "Submit")

# Load the initial data into a reactive value when the app starts
data = reactive.value(load_data())


# Append new user data on submit
@reactive.effect
@reactive.event(input.submit_button)
def submit_data():
    info = {
        "name": input.name_input(),
        "checkbox": input.checkbox(),
        "favorite_number": input.slider(),
    }
    # Update the (in-memory) data
    d = data()
    data.set(append_info(d, info))
    # Save info to persistent storage (out-of-memory)
    save_info(info)
    # Provide some user feedback
    ui.notification_show("Submitted, thanks!")


# Data grid that shows the current data
@render.data_frame
def show_results():
    return render.DataGrid(data())
