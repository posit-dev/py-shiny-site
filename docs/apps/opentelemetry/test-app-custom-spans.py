import os

# Set collection level for OpenTelemetry BEFORE imports
os.environ["SHINY_OTEL_COLLECT"] = "reactivity"

# Set AWS profile if not already set (required for Bedrock access)
if "AWS_PROFILE" not in os.environ:
    os.environ["AWS_PROFILE"] = "claude"

import time

import logfire
from opentelemetry import trace
from shiny import App, reactive, render, ui

# Configure Logfire (optional)
logfire.configure()


app_ui = ui.page_fillable(
    ui.h2("OpenTelemetry Test App"),
    ui.input_numeric("iterations", "Number of iterations:", value=3, min=1, max=10),
    ui.input_action_button("run", "Run Calculation", class_="btn-primary"),
    ui.output_text_verbatim("result"),
)


def server(input, output, session):
    # Get tracer inside server function after Logfire is configured
    tracer = trace.get_tracer(__name__)

    @reactive.calc
    @reactive.event(input.run)
    def complex_analysis():
        iterations = input.iterations()

        with tracer.start_as_current_span("process_my_data"):
            # Simulate data preprocessing
            time.sleep(1)

        with tracer.start_as_current_span("train_my_model"):
            # Simulate data preprocessing
            time.sleep(2)

        with tracer.start_as_current_span("test_my_model"):
            # Simulate data preprocessing
            time.sleep(1)

        return f"Completed {iterations} iterations in 3 seconds"

    @render.text
    def result():
        return complex_analysis()


app = App(app_ui, server)
