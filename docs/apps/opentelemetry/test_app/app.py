"""
OpenTelemetry Example with Logfire

This example demonstrates OpenTelemetry tracing in a Shiny application using
Logfire for observability.

Setup:
1. pip install shiny logfire
2. Run: logfire configure (first time only)
3. Set environment variable: export SHINY_OTEL_COLLECT=reactivity
4. Run: shiny run app.py
5. View traces at https://logfire.pydantic.dev/
"""

import logfire
import os
from datetime import datetime
from opentelemetry import trace
import asyncio

# Configure Logfire BEFORE importing Shiny
logfire.configure()

# Set collection level
os.environ["SHINY_OTEL_COLLECT"] = "reactivity"

# Now import Shiny
from shiny import App, ui, render, reactive, otel

# Get tracer for custom spans
tracer = trace.get_tracer(__name__)

app_ui = ui.page_fluid(
    ui.h2("OpenTelemetry Demo with Logfire"),
    ui.p(
        "This app demonstrates OpenTelemetry tracing. "
        "View traces at ",
        ui.a("logfire.pydantic.dev", href="https://logfire.pydantic.dev/", target="_blank")
    ),
    ui.hr(),
    ui.layout_sidebar(
        ui.sidebar(
            ui.input_slider("delay", "Simulated Delay (seconds)", 0, 3, 1, step=0.5),
            ui.input_select(
                "operation",
                "Select Operation:",
                choices={
                    "fast": "Fast Calculation",
                    "medium": "Medium Calculation",
                    "slow": "Slow Calculation",
                }
            ),
            ui.input_action_button("compute", "Compute", class_="btn-primary"),
        ),
        ui.output_text("status"),
        ui.output_text("result"),
        ui.output_text("computation_time"),
    )
)


def server(input, output, session):
    # Reactive calc that simulates a computation
    @reactive.calc
    @reactive.event(input.compute)
    async def perform_computation():
        """
        This calc will appear in traces as 'reactive:perform_computation'
        with the custom spans nested inside.
        """
        operation = input.operation()
        delay = input.delay()

        # Add custom span for data preparation
        with tracer.start_as_current_span("prepare_data") as span:
            span.set_attribute("operation.type", operation)
            span.set_attribute("operation.delay", delay)
            await asyncio.sleep(delay * 0.3)
            data = {"type": operation, "value": 42}

        # Add custom span for computation
        with tracer.start_as_current_span("compute") as span:
            await asyncio.sleep(delay * 0.7)

            if operation == "fast":
                result = data["value"] * 2
            elif operation == "medium":
                result = data["value"] ** 2
            else:  # slow
                result = sum(i for i in range(data["value"]))

            span.set_attribute("computation.result", result)

        return {
            "result": result,
            "operation": operation,
            "delay": delay,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }

    @render.text
    def status():
        """This output will appear as 'output:status' in traces"""
        return f"Ready to compute. Last update: {datetime.now().strftime('%H:%M:%S')}"

    @render.text
    async def result():
        """
        This output will appear as 'output:result' in traces.
        Note: It depends on perform_computation() but won't trigger a re-execution
        because of reactive caching.
        """
        data = await perform_computation()
        return f"Result: {data['result']} (using {data['operation']} operation)"

    @render.text
    async def computation_time():
        """Another output depending on the same calc - also appears in traces"""
        data = await perform_computation()
        return f"Computed at {data['timestamp']} with {data['delay']}s delay"


app = App(app_ui, server)
