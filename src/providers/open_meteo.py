import requests


WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
AIR_QUALITY_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"

TIMEOUT_SECONDS = 15


class OpenMeteoWeatherProvider:
    name = "open-meteo"

    def get_forecast(self, latitude, longitude):
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": (
                "temperature_2m,"
                "relative_humidity_2m,"
                "apparent_temperature,"
                "precipitation,"
                "rain,"
                "weather_code,"
                "surface_pressure,"
                "wind_speed_10m,"
                "wind_direction_10m"
            ),
            "hourly": (
                "temperature_2m,"
                "relative_humidity_2m,"
                "apparent_temperature,"
                "precipitation_probability,"
                "precipitation,"
                "rain,"
                "weather_code,"
                "surface_pressure,"
                "wind_speed_10m,"
                "wind_direction_10m,"
                "boundary_layer_height"
            ),
            "forecast_days": 3,
            "timezone": "auto",
        }

        response = requests.get(
            WEATHER_URL,
            params=params,
            timeout=TIMEOUT_SECONDS,
        )
        response.raise_for_status()

        data = response.json()
        data["_provider"] = self.name

        # AIR-COUPLE uses pressure_msl in the UI.
        current = data.get("current") or {}
        if current.get("pressure_msl") is None:
            current["pressure_msl"] = current.get("surface_pressure")
        data["current"] = current

        hourly = data.get("hourly") or {}
        if "pressure_msl" not in hourly and "surface_pressure" in hourly:
            hourly["pressure_msl"] = hourly["surface_pressure"]
        if "pbl_height" not in hourly and "boundary_layer_height" in hourly:
            hourly["pbl_height"] = hourly["boundary_layer_height"]
        data["hourly"] = hourly

        return data


class OpenMeteoAirQualityProvider:
    name = "open-meteo"

    def get_air_quality(self, latitude, longitude):
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": (
                "pm10,"
                "pm2_5,"
                "carbon_monoxide,"
                "nitrogen_dioxide,"
                "sulphur_dioxide,"
                "ozone,"
                "us_aqi"
            ),
            "forecast_days": 3,
            "timezone": "auto",
        }

        response = requests.get(
            AIR_QUALITY_URL,
            params=params,
            timeout=TIMEOUT_SECONDS,
        )
        response.raise_for_status()

        data = response.json()
        data["_provider"] = self.name
        return data
