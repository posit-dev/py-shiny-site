from shiny import reactive
from shiny.express import input, render, ui

# Add Font Awesome CSS in the head section
ui.head_content(
    ui.HTML(
        '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/css/all.min.css">'
    )
)

# Set page title
ui.page_opts(fillable=True)


# Create a card to hold the action link
with ui.card(full_screen=True, height="300px", id="card1"):
    ui.card_header("Action Link Demo")

    # Create an action link with an icon
    ui.input_action_link(
        id="demo_link",
        label="Click Me!",
        icon=ui.tags.i(class_="fa-solid fa-shield-halved"),
    )

    # Display the click count
    @render.text
    def link_clicks():
        count = input.demo_link() or 0
        return f"The link has been clicked {count} times"
