from datetime import datetime, timezone
from flask import Flask, render_template, request, jsonify

from src.location import get_location
from src.weather_service import get_weather_forecast
from src.air_quality_service import get_air_quality
from src.coupling_engine import build_coupling_forecast
from src.risk_engine import calculate_overall_risk


app = Flask(__name__)

DEFAULT_LOCATION = {
    "name": "Delhi",
    "latitude": 28.6139,
    "longitude": 77.2090,
}


def _first_value(value):
    """Return the first value from a list-like API field, otherwise the value."""
    if isinstance(value, (list, tuple)):
        return value[0] if value else None
    return value


def _number(value):
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _current_index(hourly, reference_time=None):
    """Choose the hourly point nearest to the provider's current time."""
    times = hourly.get("time") or []
    if not isinstance(times, list) or not times:
        return 0

    now = _parse_time(reference_time) if reference_time is not None else datetime.now(timezone.utc)
    best_index = 0
    best_delta = None

    for i, raw_time in enumerate(times):
        try:
            text = str(raw_time).replace("Z", "+00:00")
            point = datetime.fromisoformat(text)
            if point.tzinfo is None:
                point = point.replace(tzinfo=timezone.utc)
            delta = abs((point - now).total_seconds())
            if best_delta is None or delta < best_delta:
                best_delta = delta
                best_index = i
        except (TypeError, ValueError):
            continue

    return best_index


def _series_value(hourly, keys, index):
    for key in keys:
        values = hourly.get(key)
        if isinstance(values, list):
            if 0 <= index < len(values):
                value = values[index]
                if value is not None:
                    return value
        elif values is not None:
            return values
    return None


def _normalize_weather(weather):
    """
    Normalize provider field names used by the dashboard/coupling engine.
    Open-Meteo exposes surface_pressure and boundary_layer_height, while
    AIR-COUPLE's UI uses pressure_msl and pbl_height.
    """
    weather = weather or {}
    current = weather.get("current") or {}
    hourly = weather.get("hourly") or {}

    if current.get("pressure_msl") is None and current.get("surface_pressure") is not None:
        current["pressure_msl"] = current.get("surface_pressure")

    # Keep the original provider response intact while exposing the
    # dashboard's preferred names.
    if isinstance(hourly.get("surface_pressure"), list):
        hourly.setdefault("pressure_msl", hourly.get("surface_pressure"))

    if isinstance(hourly.get("boundary_layer_height"), list):
        hourly.setdefault("pbl_height", hourly.get("boundary_layer_height"))

    weather["current"] = current
    weather["hourly"] = hourly
    return weather


def _parse_time(value):
    if value is None:
        return None
    try:
        text = str(value).strip().replace("Z", "+00:00")
        return datetime.fromisoformat(text)
    except (TypeError, ValueError):
        return None


def _nearest_series_index(times, target, max_seconds=5400):
    if not isinstance(times, list) or not times:
        return None

    target_dt = _parse_time(target)
    if target_dt is None:
        return None

    best_index = None
    best_delta = None

    for i, raw in enumerate(times):
        dt = _parse_time(raw)
        if dt is None:
            continue

        try:
            delta = abs((dt - target_dt).total_seconds())
        except TypeError:
            # Handle one side being naive and the other offset-aware.
            if dt.tzinfo is None and target_dt.tzinfo is not None:
                dt = dt.replace(tzinfo=target_dt.tzinfo)
            elif target_dt.tzinfo is None and dt.tzinfo is not None:
                target_dt = target_dt.replace(tzinfo=dt.tzinfo)
            delta = abs((dt - target_dt).total_seconds())

        if best_delta is None or delta < best_delta:
            best_delta = delta
            best_index = i

    if best_index is None or best_delta > max_seconds:
        return None

    return best_index


def _value_at_time(series, timestamp, keys):
    series = series or {}
    times = series.get("time") or []
    index = _nearest_series_index(times, timestamp)
    if index is None:
        return None

    for key in keys:
        values = series.get(key)
        if isinstance(values, list) and index < len(values):
            value = values[index]
            if value is not None:
                return value

    return None


def _enrich_coupling_forecast(forecast, weather, air_quality):
    """
    Make every coupling point carry the pollutant + meteorological values
    consumed by the frontend.

    The coupling engine owns the dispersion/accumulation logic. This layer
    only joins the already-fetched weather and air-quality time series to
    those coupling points, so charts/table/best-window all use real data.
    """
    forecast = list(forecast or [])
    weather_hourly = (weather or {}).get("hourly") or {}
    air_hourly = (air_quality or {}).get("hourly") or {}

    weather_times = weather_hourly.get("time") or []
    air_times = air_hourly.get("time") or []

    for item in forecast:
        timestamp = item.get("time")
        w_index = _nearest_series_index(weather_times, timestamp)
        a_index = _nearest_series_index(air_times, timestamp)

        def series_value(series, index, *keys):
            if index is None:
                return None
            for key in keys:
                values = series.get(key)
                if isinstance(values, list) and index < len(values):
                    value = values[index]
                    if value is not None:
                        return value
            return None

        temperature = series_value(
            weather_hourly, w_index, "temperature_2m"
        )
        wind = series_value(
            weather_hourly, w_index, "wind_speed_10m"
        )
        pbl = series_value(
            weather_hourly, w_index,
            "boundary_layer_height", "pbl_height"
        )

        pm25 = series_value(
            air_hourly, a_index, "pm2_5", "pm25", "pm2.5"
        )
        pm10 = series_value(
            air_hourly, a_index, "pm10"
        )
        us_aqi = series_value(
            air_hourly, a_index, "us_aqi"
        )

        # Do not replace a valid engine value. Replace only missing/zero
        # PBL values because 0 m is not a meaningful atmospheric boundary
        # layer value for this dashboard.
        if item.get("temperature") is None and temperature is not None:
            item["temperature"] = temperature
        if item.get("wind_speed") is None and wind is not None:
            item["wind_speed"] = wind
        if (
            item.get("pbl_height") is None
            or _number(item.get("pbl_height")) == 0
        ) and pbl is not None:
            item["pbl_height"] = pbl

        if item.get("pm25") is None and pm25 is not None:
            item["pm25"] = pm25
        if item.get("pm10") is None and pm10 is not None:
            item["pm10"] = pm10

        if us_aqi is not None:
            item["aqi"] = {
                "aqi": us_aqi,
                "category": _aqi_category(us_aqi),
            }
        elif not item.get("aqi"):
            item["aqi"] = {
                "aqi": None,
                "category": "Unknown",
            }

    return forecast


def _extract_current_air(air_quality, reference_time=None):
    """
    Normalize provider data into the exact fields consumed by index.html:
    pm25, pm10, no2, ozone.
    """
    air_quality = air_quality or {}
    current = air_quality.get("current") or {}
    hourly = air_quality.get("hourly") or {}

    index = _current_index(hourly, reference_time)

    def current_or_hourly(current_keys, hourly_keys):
        for key in current_keys:
            if current.get(key) is not None:
                return current.get(key)
        return _series_value(hourly, hourly_keys, index)

    return {
        "pm25": current_or_hourly(
            ["pm2_5", "pm25", "pm2.5"],
            ["pm2_5", "pm25", "pm2.5"],
        ),
        "pm10": current_or_hourly(
            ["pm10"],
            ["pm10"],
        ),
        "no2": current_or_hourly(
            ["nitrogen_dioxide", "no2"],
            ["nitrogen_dioxide", "no2"],
        ),
        "ozone": current_or_hourly(
            ["ozone", "o3"],
            ["ozone", "o3"],
        ),
    }


def _aqi_category(aqi):
    """US-AQI-style category labels used by the dashboard."""
    value = _number(aqi)
    if value is None:
        return "Unknown"
    if value <= 50:
        return "Good"
    if value <= 100:
        return "Moderate"
    if value <= 150:
        return "Unhealthy for Sensitive Groups"
    if value <= 200:
        return "Unhealthy"
    if value <= 300:
        return "Very Unhealthy"
    return "Hazardous"


def _extract_current_aqi(air_quality, reference_time=None):
    """
    Normalize AQI from common Open-Meteo/provider field names.
    Prefer US AQI, then generic AQI, then European AQI.
    """
    air_quality = air_quality or {}
    current = air_quality.get("current") or {}
    hourly = air_quality.get("hourly") or {}
    index = _current_index(hourly, reference_time)

    for key in ("us_aqi", "aqi", "european_aqi"):
        if current.get(key) is not None:
            value = current.get(key)
            return {
                "aqi": value,
                "category": _aqi_category(value),
            }

    for key in ("us_aqi", "aqi", "european_aqi"):
        value = _series_value(hourly, [key], index)
        if value is not None:
            return {
                "aqi": value,
                "category": _aqi_category(value),
            }

    return {"aqi": None, "category": "Unknown"}


def _build_payload(location, weather, air_quality):
    weather = _normalize_weather(weather)
    air_quality = air_quality or {}

    coupling_forecast = build_coupling_forecast(weather, air_quality)
    coupling_forecast = _enrich_coupling_forecast(
        coupling_forecast,
        weather,
        air_quality,
    )

    current_weather = weather.get("current") or {}
    reference_time = current_weather.get("time")
    current_air = _extract_current_air(air_quality, reference_time)
    current_aqi = _extract_current_aqi(air_quality, reference_time)

    risk = calculate_overall_risk(
        pm25=_number(current_air.get("pm25")),
        pm10=_number(current_air.get("pm10")),
        temperature=_number(current_weather.get("temperature_2m")),
        wind_speed=_number(current_weather.get("wind_speed_10m")),
    )

    return {
        "success": True,
        "location": location or {},
        "latitude": float(location["latitude"]),
        "longitude": float(location["longitude"]),
        "weather": weather,
        "air_quality": air_quality,
        "current_air": current_air,
        "current_aqi": current_aqi,
        "coupling_forecast": coupling_forecast or [],
        "risk": risk,
        "providers": {
            "weather": weather.get("_provider", "unknown"),
            "air_quality": air_quality.get("_provider", "unknown"),
        },
    }


def _load_environment(location):
    latitude = float(location["latitude"])
    longitude = float(location["longitude"])

    weather = get_weather_forecast(latitude, longitude)
    air_quality = get_air_quality(latitude, longitude)

    return _build_payload(location, weather, air_quality)


def _voice_answer(question, payload):
    """
    Deterministic voice response based on the same dashboard data.
    This avoids inventing an external AI dependency while making the
    frontend's /api/voice-question contract functional.
    """
    text = (question or "").strip().lower()

    weather = payload.get("weather") or {}
    current_weather = weather.get("current") or {}
    air = payload.get("current_air") or {}
    aqi = payload.get("current_aqi") or {}
    forecast = payload.get("coupling_forecast") or []

    location_name = (payload.get("location") or {}).get("name", "this location")
    temperature = current_weather.get("temperature_2m")
    humidity = current_weather.get("relative_humidity_2m")
    wind = current_weather.get("wind_speed_10m")
    pressure = current_weather.get("pressure_msl")

    def fmt(value, suffix=""):
        return "--" if value is None else f"{value}{suffix}"

    aqi_value = aqi.get("aqi")
    category = aqi.get("category", "Unknown")

    if any(word in text for word in ("air", "aqi", "pollution", "pm2", "pm2.5", "pm10", "quality")):
        return (
            f"In {location_name}, the current AQI is {fmt(aqi_value)}, "
            f"category {category}. PM2.5 is {fmt(air.get('pm25'), ' µg/m³')}, "
            f"PM10 is {fmt(air.get('pm10'), ' µg/m³')}, and NO₂ is "
            f"{fmt(air.get('no2'), ' µg/m³')}."
        )

    if any(word in text for word in ("temperature", "weather", "hot", "cold", "humid", "humidity", "wind", "pressure")):
        return (
            f"In {location_name}, the current temperature is {fmt(temperature, ' °C')}, "
            f"humidity is {fmt(humidity, '%')}, wind is {fmt(wind, ' km/h')}, "
            f"and pressure is {fmt(pressure, ' hPa')}."
        )

    if any(word in text for word in ("outside", "walk", "walking", "run", "running", "cycle", "cycling", "exercise")):
        if aqi_value is None:
            return "The current AQI is unavailable, so I cannot give a reliable outdoor recommendation right now."
        if float(aqi_value) <= 50:
            return "Outdoor conditions are generally favorable right now, based on the current AQI."
        if float(aqi_value) <= 100:
            return "Outdoor activity is possible, but consider shorter or lower-intensity exposure if pollution bothers you."
        if float(aqi_value) <= 150:
            return "Air pollution is elevated. Consider reducing prolonged outdoor exposure, especially for strenuous activity."
        return "Air pollution is high. Avoid prolonged or strenuous outdoor exposure while pollution remains elevated."

    if any(word in text for word in ("forecast", "next", "later", "tomorrow", "trend")):
        if not forecast:
            return "The coupled forecast is currently unavailable."
        first = forecast[0]
        dispersion = (first.get("dispersion") or {}).get("level", "unknown")
        accumulation = (first.get("accumulation") or {}).get("level", "unknown")
        return (
            f"The near-term coupled forecast shows {dispersion.lower()} dispersion "
            f"and {accumulation.lower()} accumulation potential."
        )

    return (
        f"For {location_name}, I can report the current weather, air quality, "
        f"AQI, pollution levels, or the near-term coupled forecast. "
        f"Current AQI is {fmt(aqi_value)} and temperature is {fmt(temperature, ' °C')}."
    )


@app.route("/", methods=["GET", "POST"])
def home():
    location = dict(DEFAULT_LOCATION)
    weather = None
    air_quality = None
    current_air = {}
    current_aqi = {"aqi": None, "category": "Unknown"}
    coupling_forecast = []
    risk = None
    error = None
    initial_data = None

    if request.method == "POST":
        city = request.form.get("city", "").strip()

        if not city:
            error = "Please enter a city name."
        else:
            try:
                found = get_location(city)

                if found is None:
                    location = None
                    error = "Location not found."
                else:
                    location = found
                    initial_data = _load_environment(location)
            except Exception as exc:
                print(f"Home request error: {type(exc).__name__}: {exc}")
                error = str(exc)

    elif request.method == "GET":
        try:
            initial_data = _load_environment(location)
        except Exception as exc:
            print(f"Initial data load error: {type(exc).__name__}: {exc}")
            error = str(exc)

    if initial_data:
        weather = initial_data.get("weather")
        air_quality = initial_data.get("air_quality")
        current_air = initial_data.get("current_air") or {}
        current_aqi = initial_data.get("current_aqi") or current_aqi
        coupling_forecast = initial_data.get("coupling_forecast") or []
        risk = initial_data.get("risk")

    return render_template(
        "index.html",
        location=location,
        weather=weather,
        air_quality=air_quality,
        current_air=current_air,
        current_aqi=current_aqi,
        coupling_forecast=coupling_forecast,
        risk=risk,
        error=error,
        initial_data=initial_data,
    )


@app.route("/api/location-data", methods=["POST"])
def location_data():
    try:
        data = request.get_json(silent=True) or {}

        if "latitude" not in data or "longitude" not in data:
            return jsonify({
                "success": False,
                "error": "Latitude and longitude are required.",
            }), 400

        latitude = float(data["latitude"])
        longitude = float(data["longitude"])

        if not (-90 <= latitude <= 90):
            return jsonify({"success": False, "error": "Invalid latitude."}), 400

        if not (-180 <= longitude <= 180):
            return jsonify({"success": False, "error": "Invalid longitude."}), 400

        print(f"Getting environmental data for: {latitude}, {longitude}")

        location = {
            "name": str(data.get("location") or "Selected location"),
            "latitude": latitude,
            "longitude": longitude,
        }

        payload = _load_environment(location)
        return jsonify(payload)

    except KeyError as exc:
        return jsonify({
            "success": False,
            "error": f"Missing data field: {exc}",
        }), 502

    except Exception as exc:
        print("=" * 60)
        print("LOCATION API ERROR")
        print(type(exc).__name__)
        print(str(exc))
        print("=" * 60)

        return jsonify({
            "success": False,
            "error": str(exc),
            "error_type": type(exc).__name__,
        }), 500


@app.route("/api/voice-question", methods=["POST"])
def voice_question():
    try:
        data = request.get_json(silent=True) or {}
        question = str(data.get("question") or "").strip()

        if not question:
            return jsonify({
                "success": False,
                "error": "A voice question is required.",
            }), 400

        if "latitude" not in data or "longitude" not in data:
            return jsonify({
                "success": False,
                "error": "Latitude and longitude are required.",
            }), 400

        latitude = float(data["latitude"])
        longitude = float(data["longitude"])

        if not (-90 <= latitude <= 90):
            return jsonify({"success": False, "error": "Invalid latitude."}), 400

        if not (-180 <= longitude <= 180):
            return jsonify({"success": False, "error": "Invalid longitude."}), 400

        location = {
            "name": str(data.get("location") or "Selected location"),
            "latitude": latitude,
            "longitude": longitude,
        }

        payload = _load_environment(location)
        answer = _voice_answer(question, payload)

        return jsonify({
            "success": True,
            "result": {
                "answer": answer,
            },
        })

    except Exception as exc:
        print(f"VOICE API ERROR: {type(exc).__name__}: {exc}")
        return jsonify({
            "success": False,
            "error": str(exc),
            "error_type": type(exc).__name__,
        }), 500


if __name__ == "__main__":
    print("=" * 60)
    print("AIR-COUPLE")
    print("Starting Flask server...")
    print("=" * 60)
    app.run(debug=True)
