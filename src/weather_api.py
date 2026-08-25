import requests


BASE_URL = "https://api.open-meteo.com/v1/forecast"


def get_weather_forecast(latitude, longitude):
    """
    Get weather, boundary-layer and lower-atmosphere
    information for the selected location.

    This provides the meteorological inputs used by
    the pollution-weather coupling layer.
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
            "precipitation,"
            "boundary_layer_height"
        ),

        "hourly": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "pressure_msl,"
            "wind_speed_10m,"
            "wind_direction_10m,"
            "precipitation,"
            "boundary_layer_height,"
            "temperature_1000hPa,"
            "temperature_925hPa,"
            "geopotential_height_1000hPa,"
            "geopotential_height_925hPa"
        ),

        "forecast_days": 7,

        "timezone": "auto"

    }


    response = requests.get(
        BASE_URL,
        params=params,
        timeout=30
    )


    response.raise_for_status()


    return response.json()