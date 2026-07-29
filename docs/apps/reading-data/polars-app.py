import polars as pl
from shiny import reactive
from shiny.express import input, render, ui

# Use `scan_*` instead of `read_*` to use the lazy API
dat = pl.scan_parquet("./daily_weather.parquet")

with ui.sidebar():
    ui.input_checkbox_group(
        "season",
        "Season",
        choices=["Summer", "Winter", "Fall", "Spring"],
        selected="Summer",
    )
    # Import just the unique city names for our selectize input
    cities = dat.select("city_name").unique().collect().to_series().to_list()
    ui.input_selectize("city", "City", choices=cities)


# Store manipulation in a reactive calc
# (convenient for writing once and using in multiple places)
@reactive.calc
def filtered_dat():
    return dat.filter(pl.col("city_name") == input.city()).filter(
        pl.col("season").is_in(input.season())
    )


# Display the filtered data
@render.data_frame
def results_df():
    return filtered_dat().collect()
