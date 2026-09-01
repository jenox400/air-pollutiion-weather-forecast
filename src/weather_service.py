import os

from src.providers.open_meteo import OpenMeteoWeatherProvider


PROVIDERS = {
    "open-meteo": OpenMeteoWeatherProvider,
}


def get_weather_provider():
    provider_name = os.getenv(
        "AIRCOUPLE_WEATHER_PROVIDER",
        "open-meteo",
    ).strip().lower()

    provider_class = PROVIDERS.get(provider_name)

    if provider_class is None:
        supported = ", ".join(sorted(PROVIDERS))
        raise ValueError(
            f"Unsupported weather provider '{provider_name}'. "
            f"Supported providers: {supported}"
        )

    return provider_class()


def get_weather_forecast(latitude, longitude):
    provider = get_weather_provider()
    return provider.get_forecast(latitude, longitude)
