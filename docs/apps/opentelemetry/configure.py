import os

import logfire


def configure(ai_tracing: bool = False, logfire_config: bool = True):
    """
    Configure OpenTelemetry instrumentation and Logfire for the Shiny app.

    Parameters:
    - ai_tracing: Whether to enable automatic tracing for AI interactions (default: True)
    - logfire_config: Whether to configure Logfire (default: True)
    """

    # Set collection level for OpenTelemetry BEFORE imports
    os.environ["SHINY_OTEL_COLLECT"] = "reactivity"

    # Set AWS profile if not already set (required for Bedrock access)
    if "AWS_PROFILE" not in os.environ:
        os.environ["AWS_PROFILE"] = "claude"

    # Configure Logfire (optional)
    if logfire_config:
        logfire.configure()

    # Instrument chatlas/Anthropic for automatic tracing
    if ai_tracing:
        from opentelemetry.instrumentation.anthropic import AnthropicInstrumentor

        AnthropicInstrumentor().instrument()
