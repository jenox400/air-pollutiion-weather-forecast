from flask import Flask, render_template, request, jsonify

from src.risk_engine import calculate_overall_risk
from src.location import get_location
from src.weather_api import get_weather_forecast
from src.air_quality_api import get_air_quality
from src.coupling_engine import build_coupling_forecast
from src.aqi import calculate_aqi


app = Flask(__name__)


# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def safe_float(value, default=None):
    """
    Safely convert a value to float.
    """

    try:
        if value is None:
            return default

        return float(value)

    except (TypeError, ValueError):
        return default


def get_first_value(data, key):
    """
    Get the first available value from an hourly API dataset.
    """

    try:

        values = data.get(key, [])

        if not values:
            return None

        return values[0]

    except (AttributeError, IndexError):

        return None


def get_current_air_quality(air_quality):
    """
    Get the first available hourly air-quality values.

    The air-quality API returns hourly data, while the
    weather API has a dedicated current object.

    For the dashboard we use the first available hourly
    observation as the current display value.
    """

    hourly = air_quality.get(
        "hourly",
        {}
    )

    return {

        "pm25": get_first_value(
            hourly,
            "pm2_5"
        ),

        "pm10": get_first_value(
            hourly,
            "pm10"
        ),

        "no2": get_first_value(
            hourly,
            "nitrogen_dioxide"
        ),

        "ozone": get_first_value(
            hourly,
            "ozone"
        ),

        "so2": get_first_value(
            hourly,
            "sulphur_dioxide"
        )

    }


def calculate_current_aqi(air_quality):
    """
    Calculate the current/display AQI from available
    pollutant concentrations.
    """

    current_air = get_current_air_quality(
        air_quality
    )

    return calculate_aqi(

        pm25=current_air["pm25"],

        pm10=current_air["pm10"],

        no2=current_air["no2"],

        ozone=current_air["ozone"]

    )


# ==========================================================
# HOME PAGE
# ==========================================================

@app.route("/", methods=["GET", "POST"])
def home():

    location = None

    weather = None

    air_quality = None

    coupling_forecast = None

    current_aqi = None

    risk = None

    error = None


    # ------------------------------------------------------
    # CITY SEARCH
    # ------------------------------------------------------

    if request.method == "POST":

        city = request.form.get(
            "city",
            ""
        ).strip()


        if not city:

            error = "Please enter a city name."


        else:

            try:

                # ==========================================
                # FIND LOCATION
                # ==========================================

                location = get_location(
                    city
                )


                if location is None:

                    error = (
                        "Location not found. "
                        "Please try another city."
                    )


                else:

                    latitude = float(
                        location["latitude"]
                    )

                    longitude = float(
                        location["longitude"]
                    )


                    # ======================================
                    # WEATHER
                    # ======================================

                    print(
                        "Fetching weather..."
                    )


                    weather = get_weather_forecast(
                        latitude,
                        longitude
                    )


                    # ======================================
                    # AIR QUALITY
                    # ======================================

                    print(
                        "Fetching air quality..."
                    )


                    air_quality = get_air_quality(
                        latitude,
                        longitude
                    )


                    # ======================================
                    # COUPLING ENGINE
                    # ======================================

                    print(
                        "Building coupling forecast..."
                    )


                    coupling_forecast = (
                        build_coupling_forecast(
                            weather,
                            air_quality
                        )
                    )


                    # ======================================
                    # CURRENT AQI
                    # ======================================

                    current_aqi = (
                        calculate_current_aqi(
                            air_quality
                        )
                    )


                    # ======================================
                    # CURRENT WEATHER
                    # ======================================

                    current_weather = (
                        weather.get(
                            "current",
                            {}
                        )
                    )


                    current_air = (
                        get_current_air_quality(
                            air_quality
                        )
                    )


                    # ======================================
                    # ENVIRONMENTAL RISK
                    # ======================================

                    risk = calculate_overall_risk(

                        pm25=safe_float(
                            current_air["pm25"],
                            0
                        ),

                        pm10=safe_float(
                            current_air["pm10"],
                            0
                        ),

                        temperature=safe_float(
                            current_weather.get(
                                "temperature_2m"
                            ),
                            0
                        ),

                        wind_speed=safe_float(
                            current_weather.get(
                                "wind_speed_10m"
                            ),
                            0
                        )

                    )


            except Exception as e:

                print()
                print(
                    "=" * 60
                )
                print(
                    "HOME PAGE ERROR"
                )
                print(
                    type(e).__name__
                )
                print(
                    str(e)
                )
                print(
                    "=" * 60
                )


                error = str(e)


    # ------------------------------------------------------
    # RENDER WEBSITE
    # ------------------------------------------------------

    return render_template(

        "index.html",

        location=location,

        weather=weather,

        air_quality=air_quality,

        coupling_forecast=coupling_forecast,

        current_aqi=current_aqi,

        risk=risk,

        error=error

    )


# ==========================================================
# LOCATION DATA API
# ==========================================================

@app.route(
    "/api/location-data",
    methods=["POST"]
)
def location_data():

    try:

        # ==================================================
        # READ REQUEST
        # ==================================================

        data = request.get_json()


        if not data:

            return jsonify({

                "success": False,

                "error":
                    "No location data received."

            }), 400


        # ==================================================
        # GET COORDINATES
        # ==================================================

        if "latitude" not in data:

            return jsonify({

                "success": False,

                "error":
                    "Latitude is required."

            }), 400


        if "longitude" not in data:

            return jsonify({

                "success": False,

                "error":
                    "Longitude is required."

            }), 400


        latitude = float(
            data["latitude"]
        )


        longitude = float(
            data["longitude"]
        )


        print()
        print(
            "=" * 60
        )

        print(
            "LOCATION REQUEST"
        )

        print(
            f"Latitude: {latitude}"
        )

        print(
            f"Longitude: {longitude}"
        )

        print(
            "=" * 60
        )


        # ==================================================
        # WEATHER
        # ==================================================

        print(
            "Fetching weather..."
        )


        weather = get_weather_forecast(

            latitude,

            longitude

        )


        print(
            "Weather request successful."
        )


        # ==================================================
        # AIR QUALITY
        # ==================================================

        print(
            "Fetching air quality..."
        )


        air_quality = get_air_quality(

            latitude,

            longitude

        )


        print(
            "Air quality request successful."
        )


        # ==================================================
        # CURRENT WEATHER
        # ==================================================

        current_weather = (
            weather.get(
                "current",
                {}
            )
        )


        # ==================================================
        # CURRENT AIR QUALITY
        # ==================================================

        current_air = (
            get_current_air_quality(
                air_quality
            )
        )


        pm25 = safe_float(
            current_air["pm25"],
            0
        )


        pm10 = safe_float(
            current_air["pm10"],
            0
        )


        temperature = safe_float(
            current_weather.get(
                "temperature_2m"
            ),
            0
        )


        wind_speed = safe_float(
            current_weather.get(
                "wind_speed_10m"
            ),
            0
        )


        # ==================================================
        # RISK ENGINE
        # ==================================================

        print(
            "Calculating environmental risk..."
        )


        risk = calculate_overall_risk(

            pm25=pm25,

            pm10=pm10,

            temperature=temperature,

            wind_speed=wind_speed

        )


        # ==================================================
        # COUPLING ENGINE
        # ==================================================

        print(
            "Building 72-hour coupling forecast..."
        )


        coupling_forecast = (
            build_coupling_forecast(

                weather,

                air_quality

            )
        )


        # ==================================================
        # AQI FOR EACH FORECAST HOUR
        # ==================================================

        print(
            "Calculating forecast AQI..."
        )


        for hour in coupling_forecast:

            aqi_result = calculate_aqi(

                pm25=hour.get(
                    "pm25"
                ),

                pm10=hour.get(
                    "pm10"
                ),

                no2=hour.get(
                    "no2"
                ),

                ozone=hour.get(
                    "ozone"
                )

            )


            hour["aqi"] = aqi_result


        # ==================================================
        # CURRENT AQI
        # ==================================================

        current_aqi = calculate_aqi(

            pm25=current_air["pm25"],

            pm10=current_air["pm10"],

            no2=current_air["no2"],

            ozone=current_air["ozone"]

        )


        # ==================================================
        # RESPONSE
        # ==================================================

        print(
            "Location data prepared successfully."
        )


        return jsonify({

            "success": True,

            "latitude":
                latitude,

            "longitude":
                longitude,

            "weather":
                weather,

            "air_quality":
                air_quality,

            "current_air":
                current_air,

            "current_aqi":
                current_aqi,

            "risk":
                risk,

            "coupling_forecast":
                coupling_forecast

        })


    except ValueError as e:

        print()
        print(
            "INVALID LOCATION DATA"
        )

        print(
            str(e)
        )


        return jsonify({

            "success": False,

            "error":
                "Latitude and longitude must be valid numbers.",

            "error_type":
                "ValueError"

        }), 400


    except Exception as e:

        print()
        print(
            "=" * 60
        )

        print(
            "LOCATION API ERROR"
        )

        print(
            type(e).__name__
        )

        print(
            str(e)
        )

        print(
            "=" * 60
        )


        return jsonify({

            "success": False,

            "error":
                str(e),

            "error_type":
                type(e).__name__

        }), 500


# ==========================================================
# SIMPLE HEALTH CHECK
# ==========================================================

@app.route(
    "/health",
    methods=["GET"]
)
def health():

    return jsonify({

        "status": "ok",

        "service":
            "Air Pollution & Weather Forecast",

        "features": [

            "Weather forecast",

            "Air quality forecast",

            "Environmental risk",

            "72-hour coupling forecast",

            "AQI calculation",

            "PBL / atmospheric stability",

            "Pollution dispersion indicators"

        ]

    })


# ==========================================================
# RUN APPLICATION
# ==========================================================

if __name__ == "__main__":

    print()
    print(
        "=" * 60
    )

    print(
        "AIR POLLUTION & WEATHER FORECAST"
    )

    print(
        "Starting Flask server..."
    )

    print(
        "=" * 60
    )

    print()

    app.run(

        debug=True,

        host="127.0.0.1",

        port=5000

    )