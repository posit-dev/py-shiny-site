import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import time

import otel_config  # noqa: F401
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

    with tracer.start_as_current_span("process_my_data") as span:
        span.set_attribute("iterations", iterations)
        span.set_attribute("step", "preprocessing")
        time.sleep(1)

    with tracer.start_as_current_span("train_my_model") as span:
        span.set_attribute("iterations", iterations)
        span.set_attribute("step", "training")
        time.sleep(2)

    with tracer.start_as_current_span("test_my_model") as span:
        span.set_attribute("iterations", iterations)
        span.set_attribute("step", "testing")
        span.set_attribute("model.accuracy", 0.95)
        time.sleep(1)


@render.text
def result():
    return complex_analysis()
