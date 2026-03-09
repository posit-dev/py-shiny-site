"""
Weather Chat App with OpenTelemetry

This example demonstrates a chat-based weather app using:
- chatlas for Claude AI chat client (via AWS Bedrock)
- OpenTelemetry for tracing
- Logfire for observability

Setup:
1. pip install shiny chatlas logfire requests boto3
2. Run: logfire configure (first time only, optional)
3. Configure AWS Bedrock access:
   - Set AWS_PROFILE=claude (or your AWS profile with Bedrock access)
   - Ensure your AWS credentials have Bedrock permissions
4. Set environment variable:
   export SHINY_OTEL_COLLECT=reactivity
5. Run: shiny run app-demo-all-core.py
6. View traces at https://logfire.pydantic.dev/ (if Logfire is configured)
"""

import os

import logfire
import requests
from chatlas import ChatBedrockAnthropic
from opentelemetry import trace

# Configure Logfire BEFORE importing Shiny (skip if not configured)
try:
    logfire.configure()
except Exception:
    # If Logfire is not configured, continue without it
    pass

# Set collection level for OpenTelemetry
os.environ["SHINY_OTEL_COLLECT"] = "reactivity"

from shiny import App, reactive, render, ui

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


# UI
app_ui = ui.page_fillable(
    ui.div(
        {"style": "height: 100%; display: flex; flex-direction: column;"},
        ui.div(
            {"style": "flex: 1; overflow-y: auto; padding: 1rem;"},
            ui.output_ui("chat_messages")
        ),
        ui.div(
            {"style": "padding: 1rem; border-top: 1px solid #dee2e6;"},
            ui.input_text(
                "user_input",
                None,
                placeholder="Ask about the weather...",
                width="100%"
            ),
            ui.input_action_button("send", "Send", class_="btn-primary mt-2")
        )
    )
)


def server(input, output, session):
    # Store chat messages (separate client per session)
    messages_list = reactive.value([])

    # Initialize Claude client via AWS Bedrock with weather tool
    # Set AWS profile via environment variable
    os.environ["AWS_PROFILE"] = "claude"

    client = ChatBedrockAnthropic(
        system_prompt="Be terse.",
        model="us.anthropic.claude-sonnet-4-5-20250929-v1:0"
    )
    client.register_tool(get_weather_forecast)

    @reactive.effect
    @reactive.event(input.send)
    async def _():
        """Handle user message submission"""
        user_msg = input.user_input()
        print(f"[DEBUG] Button clicked, user_msg: {user_msg!r}")

        if not user_msg.strip():
            print("[DEBUG] Empty message, returning")
            return

        # Add user message to chat (create new list to trigger reactivity)
        messages = messages_list.get()
        new_messages = messages + [{"role": "user", "content": user_msg}]
        messages_list.set(new_messages)
        print(f"[DEBUG] User message added, total messages: {len(new_messages)}")

        # Clear input field
        ui.update_text("user_input", value="")

        # Get assistant response with OpenTelemetry tracing
        with tracer.start_as_current_span("chat_completion") as span:
            span.set_attribute("chat.user_message", user_msg)

            try:
                print(f"[DEBUG] Sending to Claude via Bedrock...")
                # chatlas expects messages in the format it can process
                # For a simple implementation, we'll send the conversation history
                response = await client.chat_async(user_msg)
                assistant_msg = response.content
                print(f"[DEBUG] Got response: {assistant_msg[:100]}...")

                span.set_attribute("chat.assistant_message", assistant_msg)

                # Add assistant response to chat (create new list)
                messages = messages_list.get()
                new_messages = messages + [{"role": "assistant", "content": assistant_msg}]
                messages_list.set(new_messages)
                print(f"[DEBUG] Assistant message added, total messages: {len(new_messages)}")

            except Exception as e:
                error_msg = f"Error: {str(e)}"
                print(f"[ERROR] Exception occurred: {e}")
                span.set_attribute("chat.error", str(e))

                # Add error message to chat (create new list)
                messages = messages_list.get()
                new_messages = messages + [{"role": "assistant", "content": error_msg}]
                messages_list.set(new_messages)

    @render.ui
    def chat_messages():
        """Render all chat messages"""
        messages = messages_list.get()

        if not messages:
            return ui.div(
                {"class": "text-muted text-center"},
                "Ask me about the weather!"
            )

        return ui.div(
            *[
                ui.div(
                    {
                        "class": "alert alert-primary" if msg["role"] == "user" else "alert alert-secondary",
                        "style": "text-align: right;" if msg["role"] == "user" else ""
                    },
                    ui.strong("You: " if msg["role"] == "user" else "Assistant: "),
                    msg["content"]
                )
                for msg in messages
            ]
        )

    # Set default prompt on app initialization
    @reactive.effect
    def _():
        ui.update_text("user_input", value="What is the weather in Atlanta, GA?")


app = App(app_ui, server)
