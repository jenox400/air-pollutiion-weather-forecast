from src.weather_api import get_weather_forecast
from src.air_quality_api import get_air_quality

from src.data_processing import (
    hourly_weather_to_dataframe,
    air_quality_to_dataframe
)

from src.database import (
    create_database,
    save_weather_data,
    save_air_quality_data
)


def collect_data(
    latitude,
    longitude
):
    """
    Fetch weather and air-quality data
    and save it into the database.
    """

    print("Starting data collection...")

    # --------------------------------
    # Create database
    # --------------------------------

    create_database()

    # --------------------------------
    # Weather
    # --------------------------------

    print("Fetching weather...")

    weather_data = get_weather_forecast(
        latitude,
        longitude
    )

    weather_df = hourly_weather_to_dataframe(
        weather_data
    )

    print(
        f"Weather records: {len(weather_df)}"
    )

    # --------------------------------
    # Air Quality
    # --------------------------------

    print("Fetching air quality...")

    air_quality_data = get_air_quality(
        latitude,
        longitude
    )

    air_quality_df = air_quality_to_dataframe(
        air_quality_data
    )

    print(
        f"Air-quality records: "
        f"{len(air_quality_df)}"
    )

    # --------------------------------
    # Save
    # --------------------------------

    print("Saving weather...")

    save_weather_data(
        weather_df,
        latitude,
        longitude
    )

    print("Weather saved.")

    print("Saving air quality...")

    save_air_quality_data(
        air_quality_df,
        latitude,
        longitude
    )

    print("Air quality saved.")

    print("Data collection completed.")