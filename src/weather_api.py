import requests


BASE_URL = "https://api.open-meteo.com/v1/forecast"


def get_weather_forecast(latitude, longitude):
    """
    Get current and hourly weather forecast
    from Open-Meteo.
    """

    params = {
        "latitude": latitude,
        "longitude": longitude,

        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "pressure_msl,"
            "wind_speed_10m,"
            "wind_direction_10m,"
            "precipitation"
        ),

        "hourly": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "pressure_msl,"
            "wind_speed_10m,"
            "wind_direction_10m,"
            "precipitation"
        ),

        "forecast_days": 7,

        "timezone": "auto"
    }

    response = requests.get(
        BASE_URL,
        params=params,
        timeout=15
    )

    response.raise_for_status()

    return response.json()