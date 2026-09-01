import sqlite3
import pandas as pd


DATABASE_PATH = "database/pollution.db"


def load_training_data():

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    query = """
    SELECT
        w.time,

        w.latitude,
        w.longitude,

        w.temperature,
        w.humidity,
        w.pressure,
        w.wind_speed,
        w.wind_direction,
        w.precipitation,

        a.pm2_5,
        a.pm10,
        a.carbon_monoxide,
        a.nitrogen_dioxide,
        a.sulphur_dioxide,
        a.ozone

    FROM weather w

    INNER JOIN air_quality a

        ON w.time = a.time
        AND w.latitude = a.latitude
        AND w.longitude = a.longitude

    ORDER BY w.time
    """

    df = pd.read_sql_query(
        query,
        connection
    )

    connection.close()

    df["time"] = pd.to_datetime(
        df["time"]
    )

    return df
def create_features(df):

    df = df.copy()

    # Time features

    df["hour"] = df["time"].dt.hour

    df["day_of_week"] = (
        df["time"].dt.dayofweek
    )

    df["month"] = (
        df["time"].dt.month
    )


    # PM2.5 historical features

    df["pm2_5_lag_1"] = (
        df["pm2_5"].shift(1)
    )

    df["pm2_5_lag_3"] = (
        df["pm2_5"].shift(3)
    )

    df["pm2_5_lag_6"] = (
        df["pm2_5"].shift(6)
    )

    df["pm2_5_lag_24"] = (
        df["pm2_5"].shift(24)
    )


    # PM10 historical features

    df["pm10_lag_1"] = (
        df["pm10"].shift(1)
    )

    df["pm10_lag_24"] = (
        df["pm10"].shift(24)
    )


    # Target: PM2.5 one hour ahead

    df["target_pm2_5_1h"] = (
        df["pm2_5"].shift(-1)
    )


    df = df.dropna()

    return df