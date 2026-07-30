from shiny.express import input, render, ui

with ui.popover(id="settings_popover", title="Plot settings"):
    ui.input_action_button("settings", "Settings", class_="mt-3")
    ui.input_slider("n", "Number of points", 1, 100, 50)  # <<
    ui.input_select("color", "Color", ["red", "green", "blue"])  # <<


@render.code
def summary():
    return f"{input.n()} points in {input.color()}"
