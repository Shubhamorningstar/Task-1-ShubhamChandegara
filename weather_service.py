"""
Live weather lookup using OpenWeatherMap (free API).
ChatGPT calls this when the user asks about weather for a specific place.
"""

import os

import requests

WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"


def get_weather(city: str) -> str:
    """
    Fetch current weather for a city and return a readable summary.
    Requires OPENWEATHER_API_KEY in your .env file (free at openweathermap.org).
    """
    api_key = os.getenv("OPENWEATHER_API_KEY")

    if not api_key:
        return (
            "Live weather is not configured. "
            "Get a free key at https://openweathermap.org/api "
            "and add OPENWEATHER_API_KEY to your .env file."
        )

    try:
        response = requests.get(
            WEATHER_API_URL,
            params={"q": city, "appid": api_key, "units": "metric"},
            timeout=10,
        )
        data = response.json()

        if response.status_code == 404:
            return f"I couldn't find weather data for '{city}'. Please check the city name and try again."

        if response.status_code != 200:
            return f"Weather service error: {data.get('message', 'Unknown error')}"

        # Build a friendly weather report
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        description = data["weather"][0]["description"].title()
        place = data["name"]
        country = data["sys"]["country"]

        return (
            f"Weather in {place}, {country}:\n"
            f"  • Condition: {description}\n"
            f"  • Temperature: {temp}°C (feels like {feels_like}°C)\n"
            f"  • Humidity: {humidity}%"
        )

    except requests.RequestException:
        return "Sorry, I couldn't reach the weather service right now. Please try again later."
