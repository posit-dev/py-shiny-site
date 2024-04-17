from shiny.express import ui

ui.page_opts(title="Dark Mode Switch in Navbar", fillable=True, id="page")

ui.nav_spacer() #<< 

with ui.nav_panel(ui.input_dark_mode()): #<< 
    pass
