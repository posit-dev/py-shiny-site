from shiny import reactive
from shiny.express import input, ui, render

ui.page_opts(full_width=True)

# Add Font Awesome CSS for icons
ui.head_content(
    ui.HTML(
        '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/css/all.min.css">'
    )
)

# Create a layout with some spacing
with ui.layout_column_wrap(width="100%"):
    with ui.card():
        ui.card_header("Action Button Examples")

        # Basic button with width parameter
        ui.input_action_button(id="btn1", label="Basic Button", width="200px")

        @render.text
        def click_count_btn1():
            return f"Button 1 clicks: {input.btn1() or 0}"

        ui.br()  # Add some spacing

        # Button with icon and disabled state
        ui.input_action_button(
            id="btn2",
            label="Disabled Button with Icon",
            icon=ui.tags.i(class_="fa-solid fa-shield-halved"),
            disabled=True,
        )

        @render.text
        def click_count_btn2():
            return f"Button 2 clicks: {input.btn2() or 0}"

        ui.br()  # Add some spacing

        # Button with custom class and style attributes
        ui.input_action_button(
            id="btn3",
            label="Styled Button",
            class_="btn-success",
            style="margin-top: 20px;",
        )

        @render.text
        def click_count_btn3():
            return f"Button 3 clicks: {input.btn3() or 0}"
