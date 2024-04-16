from shiny import ui, render, App

app_ui = ui.page_navbar( 
    ui.nav_spacer(), 
    ui.nav_control(ui.input_dark_mode()), 
    title="Dark mode switch in navbar"
) 

def server(input, output, session):
    pass

app = App(app_ui, server)
