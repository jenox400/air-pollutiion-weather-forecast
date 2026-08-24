from src.location_service import search_location
from fastapi import FastAPI
from src.weather_api import get_weather_forecast
from src.air_quality_api import get_air_quality
from src.data_processing import (
    hourly_weather_to_dataframe,
    air_quality_to_dataframe,
    merge_weather_and_air_quality
)

app = FastAPI(
    title="Air Pollution Weather Forecast API",
    version="1.0.0"
)


LATITUDE = 28.0229
LONGITUDE = 73.3119


@app.get("/")
def root():
    return {
        "message": "Air Pollution Weather Forecast API",
        "status": "running"
    }


@app.get("/api/weather")
def weather():

    data = get_weather_forecast(
        LATITUDE,
        LONGITUDE
    )

    return data


@app.get("/api/air-quality")
def air_quality():

    data = get_air_quality(
        LATITUDE,
        LONGITUDE
    )

    return data


@app.get("/api/dashboard")
def dashboard():

    weather_data = get_weather_forecast(
        LATITUDE,
        LONGITUDE
    )

    air_quality_data = get_air_quality(
        LATITUDE,
        LONGITUDE
    )

    weather_df = hourly_weather_to_dataframe(
        weather_data
    )

    air_quality_df = air_quality_to_dataframe(
        air_quality_data
    )

    merged_df = merge_weather_and_air_quality(
        weather_df,
        air_quality_df
    )

    return {
        "location": {
            "latitude": LATITUDE,
            "longitude": LONGITUDE
        },
        "current_weather": weather_data["current"],
        "current_air_quality": air_quality_data["current"],
        "forecast": merged_df.to_dict(
            orient="records"
        )
    }
@app.get("/api/search-location")
def search_city(city: str):

    locations = search_location(city)

    return {
        "query": city,
        "results": locations
    }