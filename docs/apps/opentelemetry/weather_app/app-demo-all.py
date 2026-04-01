# Setup:
# 1. Run: pip install shiny chatlas logfire requests boto3 opentelemetry-instrumentation-anthropic
# 2. Configure your AI provider of choice (here we use AWS Bedrock but you can replace
#    with the provider and auth setup of your choice)
# 3. Optional: Configure Logfire for observability:
#    - Run: logfire configure
#    - View traces at https://logfire.pydantic.dev/
# 4. Run: shiny run app-demo-all.py

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import otel_config  # noqa: F401
import requests
from chatlas import ChatBedrockAnthropic
from opentelemetry.instrumentation.anthropic import AnthropicInstrumentor
from shiny.express import ui

AnthropicInstrumentor().instrument()


def get_weather_forecast(lat: float, lon: float) -> str:
    """
    Get the weather forecast for a location using the National Weather Service API.
    """
    points_url = f"https://api.weather.gov/points/{lat},{lon}"
    headers = {"User-Agent": "ShinyWeatherApp"}

    try:
        points_response = requests.get(points_url, headers=headers, timeout=10)
        points_response.raise_for_status()
        points_data = points_response.json()

        forecast_url = points_data["properties"]["forecast"]

        forecast_response = requests.get(forecast_url, headers=headers, timeout=10)
        forecast_response.raise_for_status()
        forecast_data = forecast_response.json()

        periods = forecast_data["properties"]["periods"][:3]
        forecast_text = [
            f"{period['name']}: {period['detailedForecast']}" for period in periods
        ]

        return "\n\n".join(forecast_text)

    except requests.exceptions.Timeout:
        return "Weather service timeout. Please try again."
    except requests.exceptions.RequestException as e:
        return f"Error fetching weather: {str(e)}"
    except (KeyError, IndexError) as e:
        return f"Error parsing weather data: {str(e)}"


# Initialize Claude client
chat_client = ChatBedrockAnthropic(
    system_prompt="Be terse.", model="us.anthropic.claude-sonnet-4-5-20250929-v1:0"
)
chat_client.register_tool(get_weather_forecast)

ui.page_opts(fillable=True, fillable_mobile=True)

chat = ui.Chat(id="chat")
chat.ui(messages=["Ask me about the weather! Try: What is the weather in Atlanta, GA?"])


@chat.on_user_submit
async def handle_user_input(user_input: str):
    """
    Handle user message submission.
    Errors are automatically displayed as notifications by Shiny.
    """
    response = await chat_client.stream_async(user_input)
    await chat.append_message_stream(response)
