from shiny import reactive
from shiny.express import input, render, ui

# Set page title
ui.page_opts(full_width=True)

# Create a card to contain the switches
with ui.card(full_screen=True, height="300px", id="card1"):
    ui.card_header("Switch Demo")

    # Basic switch with default parameters
    ui.input_switch(id="switch1", label="Basic switch (default params)", value=False)
    
    # Output for switch1 state directly after the switch
    @render.text
    def switch1_state():
        return f"Switch 1 state: {input.switch1()}"

    # Switch with custom width
    ui.input_switch(
        id="switch2", label="Switch with custom width", value=True, width="300px"
    )
    
    # Output for switch2 state directly after the switch
    @render.text
    def switch2_state():
        return f"Switch 2 state: {input.switch2()}"
