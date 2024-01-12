# example and data from:
# https://ipyleaflet.readthedocs.io/en/latest/layers/geo_json.html
# https://ipyleaflet.readthedocs.io/en/latest/layers/marker.html
import json
import pathlib
import random

from ipyleaflet import GeoJSON, Map, Marker  # <<
from shiny.express import ui
from shinywidgets import render_widget  # <<

here = pathlib.Path(__file__)
with open(here.parent / "europe_110.geo.json", "r") as f:
    country_boundaries = json.load(f)


def random_color(feature):
    return {
        "color": "black",
        "fillColor": random.choice(["red", "yellow", "green", "orange"]),
    }


ui.h2("An ipyleaflet Map")


@render_widget  # <<
def map():
    map = Map(center=(50.6252978589571, 0.34580993652344), zoom=3)  # <<

    geo_json = GeoJSON(  # <<
        data=country_boundaries,  # <<
        style={  # <<
            "opacity": 1,  # <<
            "dashArray": "9",  # <<
            "fillOpacity": 0.1,  # <<
            "weight": 1,  # <<
        },
        hover_style={"color": "white", "dashArray": "0", "fillOpacity": 0.5},  # <<
        style_callback=random_color,  # <<
    )  # <<
    map.add_layer(geo_json)  # <<

    point = Marker(location=(52.204793, 0.121558), draggable=False)  # <<
    map.add_layer(point)  # <<

    return map  # <<
