from shiny import App, reactive, render, ui

# Define the UI
app_ui = ui.page_fillable(
    # Add Font Awesome CSS in the head section
    ui.tags.head(
        ui.tags.link(
            rel="stylesheet",
            href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/css/all.min.css",
        )
    ),

    # First card
    ui.card(
        ui.card_header("Action Link Demo"),
        # Create an action link with an icon
        ui.input_action_link(
            id="demo_link",
            label="Click Me!",
            icon=ui.tags.i(class_="fa-solid fa-shield-halved"),
        ),
        ui.output_text("link_clicks"),
        full_screen=True,
        height="300px",
        id="card1",
    ),
)


# Define the server
def server(input, output, session):
    @render.text
    def link_clicks():
        count = input.demo_link() or 0
        return f"The link has been clicked {count} times"

# Create and return the app
app = App(app_ui, server)
