# OpenTelemetry Example with Logfire
#
# This example demonstrates OpenTelemetry tracing in a Shiny application using
# Logfire for observability.
#
# Setup:
# 1. pip install shiny logfire
# 2. Run: logfire configure (first time only)
# 3. Run: shiny run app.py
# 4. View traces at https://logfire.pydantic.dev/

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from datetime import datetime

import otel_config  # noqa: F401
from opentelemetry import trace
from shiny import reactive
from shiny.express import input, render, ui

tracer = trace.get_tracer(__name__)

ui.page_opts(title="OpenTelemetry Demo with Logfire")

ui.h2("OpenTelemetry Demo with Logfire")
ui.p(
    "This app demonstrates OpenTelemetry tracing. ",
    "View traces at ",
    ui.a("logfire.pydantic.dev", href="https://logfire.pydantic.dev/", target="_blank"),
)
ui.hr()

with ui.layout_sidebar():
    with ui.sidebar():
        ui.input_slider("delay", "Simulated Delay (seconds)", 0, 3, 1, step=0.5)
        ui.input_select(
            "operation",
            "Select Operation:",
            choices={
                "fast": "Fast Calculation",
                "medium": "Medium Calculation",
                "slow": "Slow Calculation",
            },
        )
        ui.input_action_button("compute", "Compute", class_="btn-primary")

    @reactive.calc
    @reactive.event(input.compute)
    async def perform_computation():
        operation = input.operation()
        delay = input.delay()

        with tracer.start_as_current_span("prepare_data") as span:
            span.set_attribute("operation.type", operation)
            span.set_attribute("operation.delay", delay)
            await asyncio.sleep(delay * 0.3)
            data = {"type": operation, "value": 42}

        with tracer.start_as_current_span("compute") as span:
            await asyncio.sleep(delay * 0.7)

            if operation == "fast":
                result = data["value"] * 2
            elif operation == "medium":
                result = data["value"] ** 2
            else:
                result = sum(i for i in range(data["value"]))

            span.set_attribute("computation.result", result)

        return {
            "result": result,
            "operation": operation,
            "delay": delay,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
        }

    @render.text
    def status():
        return f"Ready to compute. Last update: {datetime.now().strftime('%H:%M:%S')}"

    @render.text
    async def result():
        data = await perform_computation()
        return f"Result: {data['result']} (using {data['operation']} operation)"

    @render.text
    async def computation_time():
        data = await perform_computation()
        return f"Computed at {data['timestamp']} with {data['delay']}s delay"
