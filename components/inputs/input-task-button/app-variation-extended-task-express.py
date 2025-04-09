import asyncio  # <<
from typing import List

import seaborn as sns
from shiny import reactive
from shiny.express import input, render, ui
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

diamonds = sns.load_dataset("diamonds")


with ui.sidebar():
    ui.input_selectize(
        "predictors",
        "Choose predictors",
        ["carat", "color", "cut", "clarity"],
        selected="carat",
        multiple=True,
    )
    ui.input_task_button("btn", "Fit Model")  # <<
    ui.input_switch("show", "Show Data Sample", True)

with ui.value_box(max_height=125):
    "Mean Square Error"

    @render.ui
    def mse():
        return f"{calc_model_mse.result():.2f}"


@render.data_frame
def diamonds_df():
    if input["show"]():
        return render.DataTable(diamonds.sample(5))


@ui.bind_task_button(button_id="btn")  # <<
@reactive.extended_task  # <<
async def calc_model_mse(colnames: List[str]) -> float:  # <<
    await asyncio.sleep(5)

    predictors = diamonds[colnames]
    response = diamonds["price"]

    selected_cat_cols = [
        x for x in colnames if x in ["color", "cut", "clarity"]
    ]

    # categorical variables selected one-hot encode / dummy variable encode
    if selected_cat_cols:
        categorical_transformer = Pipeline(
            steps=[("encoder", OneHotEncoder(drop="first"))]
        )
        preprocessor = ColumnTransformer(
            transformers=[
                ("cat", categorical_transformer, selected_cat_cols),
            ]
        )
        steps = [
            ("preprocessor", preprocessor),
            ("regressor", LinearRegression()),
        ]

    # no categorical column selected, so no one-hot/dummy encoding needed
    # we are doing this so lr is always a Pipeline object
    else:
        steps = [
            ("regressor", LinearRegression()),
        ]

    # create pipeline
    lr = Pipeline(steps=steps)

    # fit the model
    lr = lr.fit(X=predictors, y=response)

    # predict on itself
    pred = lr.predict(predictors)

    return mean_squared_error(predictors, pred)


@reactive.effect  # <<
@reactive.event(input.btn)  # <<
def btn_click():  # <<
    calc_model_mse(list(input["predictors"]()))  # <<
