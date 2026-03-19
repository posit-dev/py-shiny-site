import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from configure import configure

configure()

import time

from opentelemetry import trace
from shiny import reactive
from shiny.express import input, render, ui

tracer = trace.get_tracer(__name__)

ui.page_opts(title="OpenTelemetry Test App", fillable=True)

ui.input_numeric("iterations", "Number of iterations:", value=3, min=1, max=10)
ui.input_action_button("run", "Run Calculation", class_="btn-primary")


@reactive.calc
@reactive.event(input.run)
def complex_analysis():
    iterations = input.iterations()
    span = trace.get_current_span()
    span.set_attribute("iterations", iterations)

    # Simulate waiting for a function
    time.sleep(1)

    return f"Completed {iterations} iterations in 3 seconds"


@render.text
def result():
    return complex_analysis()
