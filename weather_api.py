import requests

OPENWEATHER_API_KEY = "YOUR_API_KEY_HERE"


def get_weather_forecast(lat: float, lon: float):
    """
    Fetch 7-day weather forecast (daily min/max temp) using OpenWeather One Call API.
    """
    url = (
        f"https://api.openweathermap.org/data/2.5/onecall"
        f"?lat={lat}&lon={lon}&exclude=minutely,hourly,alerts&units=metric"
        f"&appid={OPENWEATHER_API_KEY}"
    )

    response = requests.get(url)
    data = response.json()

    return data.get("daily", [])
