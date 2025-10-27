import ibis
from ibis import _
from shiny.express import ui, render, input, session
from shiny import reactive

# Connect to the database (quick, doesn't load data)
con = ibis.postgres.connect(
    user="", password="", host="", port=, database=""
)
dat = con.table("weather")
end_session = session.on_ended(con.disconnect)

with ui.sidebar():
    ui.input_checkbox_group(
        "season",
        "Season",
        choices=["Summer", "Winter", "Autumn", "Spring"],
        selected="Summer",
    )
    # Import just the unique city names for our selectize input
    cities = dat.select("city_name").distinct().execute()["city_name"].to_list()
    ui.input_selectize("city", "City", choices=cities)


# Store data manipulations in a reactive calculation
# (convenient when using the data in multiple places)
@reactive.calc
def filtered_dat():
    return dat.filter(
        [_.city_name == input.city(), _.season.isin(input.season())]
    )

# Display the filtered data
@render.data_frame
def results_df():
    return filtered_dat().execute()
