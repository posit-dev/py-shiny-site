import pandas as pd
from palmerpenguins import load_penguins
from shiny.express import render, ui

penguins: pd.DataFrame = load_penguins()

ui.h2("Palmer Penguins")


@render.data_frame
def penguins_df():
    return render.DataTable(
        penguins.iloc[[0, 1, 200, 201, 300, 301], :],
        # penguins,
        styles=[  # <<
            # Center the text of each cell (using Bootstrap utility class) # <<
            {  # <<
                "class": "text-center",  # <<
            },  # <<
            # Bold the first column # <<
            {  # <<
                "cols": [0],  # <<
                "style": {"font-weight": "bold"},  # <<
            },  # <<
            # Highlight the penguin colors # <<
            {
                "rows": [0, 1],  # <<
                "cols": [0],  # <<
                "style": {"background-color": "#ffdbaf"},  # <<
            },  # <<
            {  # <<
                "rows": [2, 3],  # <<
                "cols": [0],  # <<
                "style": {"background-color": "#b1d6d6"},  # <<
            },  # <<
            {  # <<
                "rows": [4, 5],  # <<
                "cols": [0],  # <<
                "style": {"background-color": "#d6a9f2"},  # <<
            },  # <<
        ],  # <<
    )
