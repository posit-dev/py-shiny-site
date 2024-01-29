from shiny.express import ui

with ui.panel_absolute(
    width="300px",  # <<
    right="50px",  # <<
    top="50px",  # <<
    draggable=True,  # <<
):  # <<
    with ui.panel_well():  # <<
        ui.h2("Draggable panel")  # <<
        "Move this panel anywhere you want."  # <<
