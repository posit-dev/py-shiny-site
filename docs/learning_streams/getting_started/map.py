import plotly.express as px

def plot_choropleth(dataframe, color_column, title):
    """
    Create a choropleth map for a specified percentage column.

    Args:
        dataframe (pd.DataFrame): The dataframe containing FIPS codes and demographic data.
        color_column (str): The column to use for coloring the map (e.g., 'white', 'black', etc.).
        title (str): The title for the map.

    Returns:
        plotly.graph_objects.Figure: The choropleth map figure.
    """
    # Ensure FIPS codes are strings and zero-padded
    dataframe['fips'] = dataframe['fips'].astype(str).str.zfill(5)

    # Create the choropleth map
    fig = px.choropleth(
        dataframe,
        geojson="https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json",
        locations='fips',  # Use the FIPS code for mapping
        color=color_column,  # The column to determine color
        color_continuous_scale="Viridis",  # Choose a color scale
        scope="usa",  # Limit the map to the United States
        labels={color_column: f"% {color_column.capitalize()} Population"},  # Legend label
        hover_name='county',  # Display county name on hover
        hover_data={'fips': False, color_column: True, 'total.pop': True}  # Show relevant data on hover
    )

    # Update layout for better visualization
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(
        title_text=title,
        title_x=0.5,  # Center the title
        geo=dict(bgcolor='rgba(0,0,0,0)')  # Transparent background
    )

    return fig
