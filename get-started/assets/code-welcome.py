import seaborn as sns
from shiny.express import input, render, ui

df = sns.load_dataset("penguins")

ui.input_slider("bins", "Number of Bins", min=5, max=20, value=15, step=1)

@render.plot(height=300)
def plot():
    sns.histplot(data=df, x="body_mass_g", bins=input.bins())
