"""
Weather Chat App with OpenTelemetry and Async Operations

This example demonstrates a chat-based weather app using:
- chatlas for Claude AI chat client (via AWS Bedrock)
- asyncio for asynchronous operations
- OpenTelemetry for tracing and logging
- Logfire for observability
- shinychat for the chat UI

Key features:
- Async weather tool that fetches data in background
- Custom tool with HTML display for formatted output
- OpenTelemetry logging within tool execution
- Session-specific chat client

Setup:
1. pip install shiny chatlas logfire httpx pandas shinychat boto3
2. Run: logfire configure (first time only, optional)
3. Configure AWS Bedrock access:
   - Set AWS_PROFILE=claude (or your AWS profile with Bedrock access)
   - Ensure your AWS credentials have Bedrock permissions
4. Set environment variable:
   export SHINY_OTEL_COLLECT=reactive_update
5. Run: shiny run app-async-all-core.py --port 8080 --launch-browser
6. View traces at https://logfire.pydantic.dev/ (if Logfire is configured)
"""

import os

import httpx
import logfire
import pandas as pd
from chatlas import ChatBedrockAnthropic
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider

# Configure Logfire BEFORE importing Shiny (skip if not configured)
try:
    logfire.configure()
except Exception:
    # If Logfire is not configured, continue without it
    pass

# Set collection level for OpenTelemetry
os.environ["SHINY_OTEL_COLLECT"] = "reactive_update"

from shiny import App, reactive, ui
from shiny.otel import suppress

# Get tracer and logger for custom spans/logs
tracer = trace.get_tracer("weather-app")


async def get_weather_forecast(lat: float, lon: float, location_name: str) -> str:
    """
    Get the weather forecast for a location using the National Weather Service API.

    This tool fetches weather data asynchronously and returns a formatted string.

    Args:
        lat: Latitude (US locations only)
        lon: Longitude (US locations only)
        location_name: Name of the location for display to the user

    Returns:
        Formatted weather forecast string (or HTML table for chatlas display)
    """
    with tracer.start_as_current_span("get_weather_forecast") as span:
        span.set_attribute("weather.latitude", lat)
        span.set_attribute("weather.longitude", lon)
        span.set_attribute("weather.location_name", location_name)

        # Log info message using OpenTelemetry
        logger = trace.get_tracer_provider()
        if isinstance(logger, TracerProvider):
            # Add event to current span (similar to otel::log_info in R)
            span.add_event(
                "Getting weather forecast",
                attributes={
                    "latitude": lat,
                    "longitude": lon,
                    "location": location_name
                }
            )

        points_url = f"https://api.weather.gov/points/{lat},{lon}"
        headers = {"User-Agent": "ShinyWeatherApp"}

        try:
            # Use httpx for async HTTP requests
            async with httpx.AsyncClient() as client:
                # Get the forecast URL for the given coordinates
                points_response = await client.get(points_url, headers=headers, timeout=10.0)
                points_response.raise_for_status()
                points_data = points_response.json()

                forecast_url = points_data["properties"]["forecast"]

                # Fetch the actual forecast
                forecast_response = await client.get(forecast_url, headers=headers, timeout=10.0)
                forecast_response.raise_for_status()
                forecast_data = forecast_response.json()

                # Extract forecast periods
                periods = forecast_data["properties"]["periods"][:7]  # Get first week

                # Create DataFrame for nice formatting
                df = pd.DataFrame([
                    {
                        "Period": period["name"],
                        "Temperature": f"{period['temperature']}°{period['temperatureUnit']}",
                        "Wind": period["windSpeed"],
                        "Forecast": period["shortForecast"],
                    }
                    for period in periods
                ])

                # Convert to HTML table
                forecast_table = df.to_html(index=False, classes="table table-striped table-sm")

                span.set_attribute("weather.periods_count", len(periods))

                # Return formatted HTML table
                return forecast_table

        except httpx.TimeoutException:
            error_msg = "Weather service timeout. Please try again."
            span.set_attribute("weather.error", error_msg)
            return error_msg
        except httpx.HTTPError as e:
            error_msg = f"HTTP error fetching weather: {str(e)}"
            span.set_attribute("weather.error", error_msg)
            return error_msg
        except (KeyError, IndexError) as e:
            error_msg = f"Error parsing weather data: {str(e)}"
            span.set_attribute("weather.error", error_msg)
            return error_msg


# UI
app_ui = ui.page_fillable(
    ui.chat_ui("chat", height="100%")
)


def server(input, output, session):
    # Set up client within server to not share the client across sessions
    # Configure AWS Bedrock with Claude
    os.environ["AWS_PROFILE"] = "claude"

    client = ChatBedrockAnthropic(
        system_prompt="Be terse.",
        model="us.anthropic.claude-sonnet-4-5-20250929-v1:0"
    )

    # Register the async weather tool
    client.register_tool(get_weather_forecast)

    # Do not collect any Shiny OTel spans/logs for the chat callbacks
    # Use suppress() context manager to disable OTel collection
    with suppress():
        # Create chat instance
        chat = ui.Chat(id="chat")

        # Define callback to run when user submits a message
        @chat.on_user_submit
        async def handle_user_input(user_input: str):
            # Get response from Claude (with tool calling)
            # chatlas will automatically call the weather tool if needed
            response = await client.chat_async(user_input)

            # Append the final response to chat
            await chat.append_message(response.content)

    # Set initial prompt after session starts (run once)
    @reactive.effect
    def _():
        chat.update_user_input(value="What is the weather in Atlanta, GA?")


app = App(app_ui, server)
