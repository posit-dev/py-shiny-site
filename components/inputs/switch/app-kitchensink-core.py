from shiny import App, render, ui

# Define the UI
app_ui = ui.page_fluid(
    # Create a card to contain the switches
    ui.card(
        ui.card_header("Switch Demo"),
        # Basic switch with default parameters
        ui.input_switch(
            id="switch1", label="Basic switch (default params)", value=False
        ),
        # Output for switch1 state
        ui.output_text("switch1_state"),

        # Switch with custom width
        ui.input_switch(
            id="switch2", label="Switch with custom width", value=True, width="300px"
        ),
        # Output for switch2 state
        ui.output_text("switch2_state"),
        full_screen=True,
        height="300px",
        id="card1",
    )
)


# Define the server
def server(input, output, session):
    @render.text
    def switch1_state():
        return f"Switch 1 state: {input.switch1()}"
    
    @render.text
    def switch2_state():
        return f"Switch 2 state: {input.switch2()}"


# Create the app
app = App(app_ui, server)
