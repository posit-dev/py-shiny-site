from shiny import reactive
from shiny.express import input, ui, render

# Sample data for states
states = {
    "East Coast": {"NY": "New York", "NJ": "New Jersey", "CT": "Connecticut"},
    "West Coast": {"WA": "Washington", "OR": "Oregon", "CA": "California"},
    "Midwest": {"MN": "Minnesota", "WI": "Wisconsin", "IA": "Iowa"},
}

# Set page options
ui.page_opts(full_width=True)

ui.h2("Input Selectize Demo")

# Basic selectize with all parameters
ui.input_selectize(
    id="state",
    label="Choose state(s):",
    choices=states,
    selected=["NY", "CA"],
    multiple=False,
    options={
        "placeholder": "Select states...",
        "plugins": ["clear_button"],
        "render": ui.js_eval(
            '{option: function(item, escape) {return "<div><strong>" + escape(item.label) + "</strong></div>";}}'
        ),
    },
)

with ui.card():
    ui.card_header("Selection Results")

    @render.text
    def selection():
        if not input.state():
            return "No states selected"
        #   multiple=False -> str  (single selected value)
        #   multiple=True  -> tuple (of selected string values, empty tuple if none selected)
        return f"You selected: {input.state()}"
