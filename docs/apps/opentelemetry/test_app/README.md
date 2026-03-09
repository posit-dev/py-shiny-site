# OpenTelemetry Example App

This example demonstrates OpenTelemetry tracing in a Shiny application using Logfire.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure Logfire (first time only):
   ```bash
   logfire configure
   ```
   Follow the prompts to authenticate and create/select a project.

3. Set the collection level:
   ```bash
   export SHINY_OTEL_COLLECT=reactivity
   ```

4. Run the app:
   ```bash
   shiny run app.py
   ```

5. Open your browser and interact with the app.

6. View traces at [logfire.pydantic.dev](https://logfire.pydantic.dev/)

## What to Look For

In the Logfire dashboard, you'll see:

- **Session span**: The overall user session
- **Reactive update span**: Each time you click "Compute"
- **Calc execution**: The `perform_computation` reactive calc
- **Custom spans**: `prepare_data` and `compute` operations
- **Output renders**: `result` and `computation_time` outputs

### Key Observations

1. **Caching**: Both outputs (`result` and `computation_time`) depend on the same calc, but the calc only runs once per button click.

2. **Custom spans**: The `prepare_data` and `compute` spans are nested inside the calc execution, showing detailed timing for each step.

3. **Attributes**: Custom attributes like `operation.type` and `computation.result` appear in the span details.

## Using with Other Backends

To use Jaeger or another OpenTelemetry backend instead of Logfire:

1. Remove the `logfire.configure()` call
2. Add standard OpenTelemetry configuration:

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

trace.set_tracer_provider(TracerProvider())
exporter = OTLPSpanExporter(endpoint="http://localhost:4317")
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(exporter))
```

3. Install the required packages:
   ```bash
   pip install opentelemetry-sdk opentelemetry-exporter-otlp
   ```
