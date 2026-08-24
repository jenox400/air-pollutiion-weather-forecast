import requests
import time


BASE_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"


def get_air_quality(latitude, longitude):

    params = {
        "latitude": latitude,
        "longitude": longitude,

        "hourly": (
            "pm2_5,"
            "pm10,"
            "carbon_monoxide,"
            "nitrogen_dioxide,"
            "sulphur_dioxide,"
            "ozone"
        ),

        "forecast_days": 7,
        "timezone": "auto"
    }

    max_attempts = 3

    for attempt in range(1, max_attempts + 1):

        try:

            print(
                f"Requesting air quality "
                f"(attempt {attempt}/{max_attempts})..."
            )

            response = requests.get(
                BASE_URL,
                params=params,
                timeout=(10, 60)
            )

            response.raise_for_status()

            data = response.json()

            print("Air quality request successful.")

            return data

        except requests.exceptions.Timeout:

            print(
                f"Air quality request timed out "
                f"on attempt {attempt}."
            )

            if attempt < max_attempts:
                print("Retrying...")
                time.sleep(3)

        except requests.exceptions.RequestException as error:

            print(
                "Air quality request failed:"
            )

            print(error)

            if attempt < max_attempts:
                print("Retrying...")
                time.sleep(3)

    raise RuntimeError(
        "Unable to retrieve air-quality data "
        "after 3 attempts."
    )