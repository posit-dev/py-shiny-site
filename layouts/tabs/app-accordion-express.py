from shiny.express import ui

with ui.accordion(id="acc", open="Section A"):  # <<
    with ui.accordion_panel("Section A"):  # <<
        "Section A content"

    with ui.accordion_panel("Section B"):  # <<
        "Section B content"

    with ui.accordion_panel("Section C"):  # <<
        "Section C content"

    with ui.accordion_panel("Section D"):  # <<
        "Section D content"

    with ui.accordion_panel("Section E"):  # <<
        "Section E content"
