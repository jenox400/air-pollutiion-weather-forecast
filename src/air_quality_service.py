import os

from src.providers.open_meteo import OpenMeteoAirQualityProvider


PROVIDERS = {
    "open-meteo": OpenMeteoAirQualityProvider,
}


def get_air_quality_provider():
    provider_name = os.getenv(
        "AIRCOUPLE_AIR_PROVIDER",
        "open-meteo",
    ).strip().lower()

    provider_class = PROVIDERS.get(provider_name)

    if provider_class is None:
        supported = ", ".join(sorted(PROVIDERS))
        raise ValueError(
            f"Unsupported air-quality provider '{provider_name}'. "
            f"Supported providers: {supported}"
        )

    return provider_class()


def get_air_quality(latitude, longitude):
    provider = get_air_quality_provider()
    return provider.get_air_quality(latitude, longitude)
