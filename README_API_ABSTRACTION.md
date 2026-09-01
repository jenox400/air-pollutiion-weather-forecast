# AIR-COUPLE API Abstraction Layer

This package adds a provider layer so the frontend does not depend on a specific weather/AQI vendor.

## Current providers

- Weather: Open-Meteo
- Air quality: Open-Meteo

## Run

Replace the project's `app.py` with the supplied `app.py`.

Copy the supplied `src` files into your project's `src` directory.

Then:

```text
python -m py_compile app.py
```

and:

```text
python app.py
```

## Change the weather provider

1. Create a new provider in:

```text
src/providers/
```

2. Implement:

```python
class MyWeatherProvider:
    name = "my-provider"

    def get_forecast(self, latitude, longitude):
        # Call the external API.
        # Convert its response to the AIR-COUPLE internal format.
        return data
```

3. Register it in `src/weather_service.py`:

```python
from src.providers.my_provider import MyWeatherProvider

PROVIDERS = {
    "open-meteo": OpenMeteoWeatherProvider,
    "my-provider": MyWeatherProvider,
}
```

4. Set:

```text
AIRCOUPLE_WEATHER_PROVIDER=my-provider
```

No frontend change is required.

## Change the air-quality provider

Use the same pattern in:

```text
src/air_quality_service.py
```

and set:

```text
AIRCOUPLE_AIR_PROVIDER=my-provider
```

## Important

The provider adapter is responsible for translating vendor-specific JSON into the format expected by AIR-COUPLE.

That is the key abstraction. The frontend only talks to Flask endpoints such as:

```text
/api/location-data
/api/voice-question
```

It does not need to know which external vendor supplies the data.
