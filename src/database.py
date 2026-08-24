import sqlite3
import pandas as pd
from pathlib import Path


DATABASE_PATH = "database/pollution.db"


def get_connection():
    """
    Create a connection to the SQLite database.
    """

    Path("database").mkdir(
        exist_ok=True
    )

    return sqlite3.connect(
        DATABASE_PATH
    )


def create_database():
    """
    Create database tables if they don't exist.
    """

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weather (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            time TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            temperature REAL,
            humidity REAL,
            pressure REAL,
            wind_speed REAL,
            wind_direction REAL,
            precipitation REAL,
            UNIQUE(time, latitude, longitude)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS air_quality (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            time TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            pm2_5 REAL,
            pm10 REAL,
            carbon_monoxide REAL,
            nitrogen_dioxide REAL,
            sulphur_dioxide REAL,
            ozone REAL,
            UNIQUE(time, latitude, longitude)
        )
    """)

    connection.commit()
    connection.close()


def save_weather_data(
    df,
    latitude,
    longitude
):
    """
    Save weather data while avoiding duplicates.
    """

    connection = get_connection()

    df = df.copy()

    df["latitude"] = latitude
    df["longitude"] = longitude

    columns = [
        "time",
        "latitude",
        "longitude",
        "temperature",
        "humidity",
        "pressure",
        "wind_speed",
        "wind_direction",
        "precipitation"
    ]

    df = df[columns]

    for _, row in df.iterrows():

        connection.execute("""
            INSERT OR IGNORE INTO weather (
                time,
                latitude,
                longitude,
                temperature,
                humidity,
                pressure,
                wind_speed,
                wind_direction,
                precipitation
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row["time"].isoformat(),
            row["latitude"],
            row["longitude"],
            row["temperature"],
            row["humidity"],
            row["pressure"],
            row["wind_speed"],
            row["wind_direction"],
            row["precipitation"]
        ))

    connection.commit()
    connection.close()


def save_air_quality_data(
    df,
    latitude,
    longitude
):
    """
    Save air-quality data while avoiding duplicates.
    """

    connection = get_connection()

    df = df.copy()

    df["latitude"] = latitude
    df["longitude"] = longitude

    columns = [
        "time",
        "latitude",
        "longitude",
        "pm2_5",
        "pm10",
        "carbon_monoxide",
        "nitrogen_dioxide",
        "sulphur_dioxide",
        "ozone"
    ]

    df = df[columns]

    for _, row in df.iterrows():

        connection.execute("""
            INSERT OR IGNORE INTO air_quality (
                time,
                latitude,
                longitude,
                pm2_5,
                pm10,
                carbon_monoxide,
                nitrogen_dioxide,
                sulphur_dioxide,
                ozone
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row["time"].isoformat(),
            row["latitude"],
            row["longitude"],
            row["pm2_5"],
            row["pm10"],
            row["carbon_monoxide"],
            row["nitrogen_dioxide"],
            row["sulphur_dioxide"],
            row["ozone"]
        ))

    connection.commit()
    connection.close()