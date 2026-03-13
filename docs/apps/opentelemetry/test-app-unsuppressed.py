import time

import logfire
from opentelemetry import trace
from shiny import App, otel, reactive, render, ui

# Configure Logfire (it will auto-configure on first use if needed)
logfire.configure()

app_ui = ui.page_fillable(
    ui.input_slider("n", "N", 0, 100, 20),
    ui.output_text_verbatim("n_squared"),
    title="My App",
)


def server(input, output, session):
    # Get tracer for custom spans
    tracer = trace.get_tracer(__name__)

    # Do not trace _Shiny_ reactive expressions within this block
    # All other otel spans/logs will still be recorded
    @reactive.calc
    def expensive_calculation():
        # Start a custom span for this calculation
        with tracer.start_as_current_span("my custom span") as span:
            span.set_attribute("step", "expensive_step")
            # Simulate an expensive operation
            time.sleep(2)

            return input.n() ** 2

    @render.text
    def n_squared():
        n_squared_val = expensive_calculation()
        return f"n * 2 = {n_squared_val}"


app = App(app_ui, server)
