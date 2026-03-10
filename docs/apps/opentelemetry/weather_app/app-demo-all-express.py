# Weather Chat App with OpenTelemetry (Express Mode)
#
# This example demonstrates a chat-based weather app using:
# - Shiny's built-in ui.Chat() component
# - chatlas for Claude AI chat client (via AWS Bedrock)
# - OpenTelemetry for tracing
# - Logfire for observability
#
# Setup:
# 1. pip install shiny chatlas logfire requests boto3 opentelemetry-instrumentation-anthropic
# 2. Configure AWS Bedrock access:
#    - Set AWS_PROFILE=claude (or your AWS profile with Bedrock access)
#    - Ensure your AWS credentials have Bedrock permissions
# 3. Set environment variables:
#    export SHINY_OTEL_COLLECT=reactivity
#    export AWS_PROFILE=claude
# 4. Optional: Configure Logfire for observability:
#    - Run: logfire configure
#    - View traces at https://logfire.pydantic.dev/
# 5. Run: shiny run app-demo-all-express.py

import os

# Set collection level for OpenTelemetry BEFORE imports
os.environ["SHINY_OTEL_COLLECT"] = "reactivity"

# Set AWS profile if not already set (required for Bedrock access)
if "AWS_PROFILE" not in os.environ:
    os.environ["AWS_PROFILE"] = "claude"

import logfire
import requests
from chatlas import ChatBedrockAnthropic
from opentelemetry import trace

# Instrumentation for our chosen chat client (Anthropic/Claude via chatlas)
from opentelemetry.instrumentation.anthropic import AnthropicInstrumentor
from shiny.express import ui

# Configure Logfire (optional)
_ = logfire.configure()

# Instrument chatlas/Anthropic for automatic tracing
_ = AnthropicInstrumentor().instrument()

# Get tracer for custom spans
tracer = trace.get_tracer(__name__)


def get_weather_forecast(lat: float, lon: float) -> str:
    """
    Get the weather forecast for a location using the National Weather Service API.

    Args:
        lat: Latitude (US locations only)
        lon: Longitude (US locations only)

    Returns:
        Weather forecast as a formatted string
    """
    with tracer.start_as_current_span("fetch_weather") as span:
        span.set_attribute("weather.latitude", lat)
        span.set_attribute("weather.longitude", lon)

        points_url = f"https://api.weather.gov/points/{lat},{lon}"
        headers = {"User-Agent": "ShinyWeatherApp"}

        try:
            # Get the forecast URL for the given coordinates
            points_response = requests.get(points_url, headers=headers, timeout=10)
            points_response.raise_for_status()
            points_data = points_response.json()

            forecast_url = points_data["properties"]["forecast"]

            # Fetch the actual forecast
            forecast_response = requests.get(forecast_url, headers=headers, timeout=10)
            forecast_response.raise_for_status()
            forecast_data = forecast_response.json()

            # Format the first 3 forecast periods
            periods = forecast_data["properties"]["periods"][:3]
            forecast_text = [
                f"{period['name']}: {period['detailedForecast']}"
                for period in periods
            ]

            result = "\n\n".join(forecast_text)
            span.set_attribute("weather.forecast_length", len(result))

            return result

        except requests.exceptions.Timeout:
            error_msg = "Weather service timeout. Please try again."
            span.set_attribute("weather.error", error_msg)
            return error_msg
        except requests.exceptions.RequestException as e:
            error_msg = f"Error fetching weather: {str(e)}"
            span.set_attribute("weather.error", error_msg)
            return error_msg
        except (KeyError, IndexError) as e:
            error_msg = f"Error parsing weather data: {str(e)}"
            span.set_attribute("weather.error", error_msg)
            return error_msg


# Initialize Claude client
chat_client = ChatBedrockAnthropic(
    system_prompt="Be terse.",
    model="us.anthropic.claude-sonnet-4-5-20250929-v1:0"
)
# Register the weather tool we defined above
chat_client.register_tool(get_weather_forecast)

# Set page options
ui.page_opts(fillable=True, fillable_mobile=True)

# Create a chat instance
chat = ui.Chat(id="chat")
chat.ui(messages=["Ask me about the weather! Try: What is the weather in Atlanta, GA?"])


@chat.on_user_submit
async def handle_user_input(user_input: str):
    """
    Handle user message submission.
    Errors are automatically displayed as notifications by Shiny.
    """
    # Send message to Claude and stream response
    # AnthropicInstrumentor automatically traces this call for Otel
    response = await chat_client.stream_async(user_input)
    await chat.append_message_stream(response)
