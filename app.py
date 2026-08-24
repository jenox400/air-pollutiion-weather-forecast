from flask import Flask, render_template, request

from src.location import get_location
from src.weather_api import get_weather_forecast
from src.air_quality_api import get_air_quality


app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def home():

    location = None
    weather = None
    air_quality = None
    error = None

    if request.method == "POST":

        city = request.form.get("city", "").strip()

        if not city:
            error = "Please enter a city name."

        else:

            try:

                # Find latitude and longitude
                location = get_location(city)

                if location is None:
                    error = "Location not found."

                else:

                    latitude = location["latitude"]
                    longitude = location["longitude"]

                    # Get weather
                    weather = get_weather_forecast(
                        latitude,
                        longitude
                    )

                    # Get air quality
                    air_quality = get_air_quality(
                        latitude,
                        longitude
                    )

            except Exception as e:

                error = str(e)

    return render_template(
        "index.html",
        location=location,
        weather=weather,
        air_quality=air_quality,
        error=error
    )


if __name__ == "__main__":
    app.run(
        debug=True
    )