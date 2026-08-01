from shiny.express import input, render, ui

ui.h4("Quarterly report")
"This heading and text are outside the navbar."

with ui.navset_bar(title="Sections", id="section"):  # <<
    with ui.nav_panel("Summary"):  # <<
        "Summary content"

    with ui.nav_panel("Details"):  # <<
        "Details content"

    ui.nav_spacer()  # <<

    with ui.nav_panel("About"):  # <<
        "About content"

ui.h6("Selected section:")


@render.code
def selected():
    return input.section()
