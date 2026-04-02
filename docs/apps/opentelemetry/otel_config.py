import os

import logfire

# Set collection level for OpenTelemetry
os.environ["SHINY_OTEL_COLLECT"] = "reactivity"

# Set up AI provider credentials (e.g., AWS_PROFILE for AWS Bedrock)
if "AWS_PROFILE" not in os.environ:
    os.environ["AWS_PROFILE"] = "claude"

# Configure Logfire (or other observability backend)
logfire.configure()
