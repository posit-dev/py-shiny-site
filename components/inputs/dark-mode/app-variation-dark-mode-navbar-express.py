from shiny.express import ui

ui.page_opts(title="Dark mode switch in navbar", fillable=True, id="page")

ui.nav_spacer()  # <<
with ui.nav_control():  # <<
    ui.input_dark_mode()  # <<
