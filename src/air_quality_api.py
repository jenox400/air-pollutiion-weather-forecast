import time
import requests


BASE_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"


def get_air_quality(latitude, longitude):

    params = {

        "latitude": latitude,
        "longitude": longitude,

        "hourly": (
            "pm2_5,"
            "pm10,"
            "nitrogen_dioxide,"
            "ozone,"
            "sulphur_dioxide"
        ),

        "forecast_days": 7,

        "timezone": "auto"

    }


    max_attempts = 3


    for attempt in range(
        1,
        max_attempts + 1
    ):

        try:

            print(
                f"Requesting air quality "
                f"(attempt {attempt}/{max_attempts})..."
            )


            response = requests.get(
                BASE_URL,
                params=params,
                timeout=30
            )


            response.raise_for_status()


            print(
                "Air quality request successful."
            )


            return response.json()


        except requests.exceptions.Timeout:

            print(
                f"Air quality request timed out "
                f"on attempt {attempt}."
            )


            if attempt < max_attempts:

                print("Retrying...")

                time.sleep(2)

            else:

                raise


        except requests.exceptions.RequestException:

            raise


    raise RuntimeError(
        "Unable to retrieve air-quality data."
    )