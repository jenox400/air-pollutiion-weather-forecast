import pandas as pd


def hourly_weather_to_dataframe(weather_data):
    """
    Convert Open-Meteo hourly weather JSON
    into a Pandas DataFrame.
    """

    hourly = weather_data["hourly"]

    df = pd.DataFrame({
        "time": hourly["time"],
        "temperature": hourly["temperature_2m"],
        "humidity": hourly["relative_humidity_2m"],
        "pressure": hourly["pressure_msl"],
        "wind_speed": hourly["wind_speed_10m"],
        "wind_direction": hourly["wind_direction_10m"],
        "precipitation": hourly["precipitation"]
    })

    df["time"] = pd.to_datetime(df["time"])

    return df


def air_quality_to_dataframe(air_quality_data):
    """
    Convert Open-Meteo hourly air-quality JSON
    into a Pandas DataFrame.
    """

    hourly = air_quality_data["hourly"]

    df = pd.DataFrame({
        "time": hourly["time"],
        "pm2_5": hourly["pm2_5"],
        "pm10": hourly["pm10"],
        "carbon_monoxide": hourly["carbon_monoxide"],
        "nitrogen_dioxide": hourly["nitrogen_dioxide"],
        "sulphur_dioxide": hourly["sulphur_dioxide"],
        "ozone": hourly["ozone"]
    })

    df["time"] = pd.to_datetime(df["time"])

    return df
def merge_weather_and_air_quality(
    weather_df,
    air_quality_df
):
    """
    Merge weather and air-quality data
    using the timestamp.
    """

    merged_df = pd.merge(
        weather_df,
        air_quality_df,
        on="time",
        how="inner"
    )

    return merged_df