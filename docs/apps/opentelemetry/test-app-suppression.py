import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from configure import configure

configure()

import time

from opentelemetry import trace
from shiny import otel, reactive
from shiny.express import input, render, ui

tracer = trace.get_tracer(__name__)

ui.page_opts(title="My App", fillable=True)

ui.input_slider("n", "N", 0, 100, 20)

with otel.suppress():

    @reactive.calc
    def expensive_calculation():
        with tracer.start_as_current_span("my custom span") as span:
            span.set_attribute("step", "expensive_step")
            time.sleep(2)
            return input.n() ** 2


@render.text
def n_squared():
    n_squared_val = expensive_calculation()
    return f"n * 2 = {n_squared_val}"
