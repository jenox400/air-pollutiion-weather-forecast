"""
Weather-Pollution Coupling Engine

Physics-informed prototype layer connecting
meteorological conditions with pollution behavior.

This is NOT a replacement for WRF-Chem or a
full chemical transport model.
"""


def safe_number(value, default=0.0):
    """Safely convert a value to float."""

    try:
        if value is None:
            return default

        return float(value)

    except (TypeError, ValueError):
        return default


def get_hourly_value(data, key, index, default=None):
    """Safely get one value from an hourly API array."""

    try:
        values = data.get(key, [])

        if index >= len(values):
            return default

        return values[index]

    except (AttributeError, TypeError, IndexError):
        return default


# ==========================================================
# ATMOSPHERIC STABILITY / INVERSION PROXY
# ==========================================================

def calculate_inversion_proxy(
    temperature_1000,
    temperature_925,
    height_1000,
    height_925
):
    """
    Estimate lower-atmosphere stability.

    Positive temperature gradient with height can indicate
    inversion-like/stable atmospheric conditions.

    This is a proxy, not a complete inversion diagnosis.
    """

    t1000 = safe_number(temperature_1000)
    t925 = safe_number(temperature_925)

    z1000 = safe_number(height_1000)
    z925 = safe_number(height_925)

    height_difference = z925 - z1000
    temperature_difference = t925 - t1000

    if height_difference <= 0:

        return {
            "gradient": None,
            "level": "Unknown",
            "score": 0,
            "message": (
                "Insufficient vertical-profile data."
            )
        }

    gradient = (
        temperature_difference /
        height_difference
    ) * 1000

    # ------------------------------------------------------
    # Classification
    # ------------------------------------------------------

    if gradient >= 2.0:

        level = "Strong"
        score = 3

        message = (
            "Strong inversion-like stability may "
            "suppress vertical mixing."
        )

    elif gradient >= 0.5:

        level = "Moderate"
        score = 2

        message = (
            "Moderate atmospheric stability may "
            "reduce vertical pollution dispersion."
        )

    elif gradient >= 0:

        level = "Weak"
        score = 1

        message = (
            "Weak stable atmospheric conditions "
            "are present."
        )

    else:

        level = "Unstable"
        score = 0

        message = (
            "The temperature structure supports "
            "stronger vertical mixing."
        )

    return {
        "gradient": round(gradient, 3),
        "level": level,
        "score": score,
        "message": message
    }


# ==========================================================
# DISPERSION SCORE
# ==========================================================

def calculate_dispersion_score(
    wind_speed,
    pbl_height,
    precipitation
):
    """
    Estimate how favorable the weather is for
    pollutant dispersion.

    Higher score = better dispersion.

    This is a simplified physics-informed indicator.
    """

    wind = safe_number(wind_speed)
    pbl = safe_number(pbl_height)
    rain = safe_number(precipitation)

    score = 0

    # ------------------------------------------------------
    # Wind contribution
    # ------------------------------------------------------

    if wind >= 15:

        score += 3

    elif wind >= 8:

        score += 2

    elif wind >= 4:

        score += 1

    # ------------------------------------------------------
    # PBL contribution
    # ------------------------------------------------------

    if pbl >= 1200:

        score += 3

    elif pbl >= 700:

        score += 2

    elif pbl >= 400:

        score += 1

    # ------------------------------------------------------
    # Rain contribution
    # ------------------------------------------------------

    if rain >= 2:

        score += 2

    elif rain > 0:

        score += 1

    # ------------------------------------------------------
    # Classification
    # ------------------------------------------------------

    if score >= 6:

        level = "High"

        message = (
            "Weather conditions are favorable "
            "for pollutant dispersion."
        )

    elif score >= 3:

        level = "Moderate"

        message = (
            "Pollution dispersion is possible, "
            "but some trapping conditions remain."
        )

    else:

        level = "Low"

        message = (
            "Weak dispersion conditions may allow "
            "pollution to accumulate near the surface."
        )

    return {
        "score": score,
        "level": level,
        "message": message
    }


# ==========================================================
# POLLUTION ACCUMULATION RISK
# ==========================================================

def calculate_accumulation_risk(
    wind_speed,
    pbl_height,
    inversion_score,
    precipitation
):
    """
    Estimate pollution accumulation potential.

    Higher score = greater accumulation potential.
    """

    wind = safe_number(wind_speed)
    pbl = safe_number(pbl_height)
    rain = safe_number(precipitation)

    score = 0

    # ------------------------------------------------------
    # Weak wind
    # ------------------------------------------------------

    if wind < 4:

        score += 2

    elif wind < 8:

        score += 1

    # ------------------------------------------------------
    # Low boundary layer
    # ------------------------------------------------------

    if pbl < 400:

        score += 3

    elif pbl < 700:

        score += 2

    elif pbl < 1200:

        score += 1

    # ------------------------------------------------------
    # Atmospheric stability
    # ------------------------------------------------------

    score += inversion_score

    # ------------------------------------------------------
    # Rain can reduce accumulation
    # ------------------------------------------------------

    if rain > 2:

        score -= 2

    score = max(0, score)

    # ------------------------------------------------------
    # Classification
    # ------------------------------------------------------

    if score >= 6:

        level = "High"

    elif score >= 3:

        level = "Moderate"

    else:

        level = "Low"

    return {
        "score": score,
        "level": level
    }


# ==========================================================
# BUILD 72-HOUR COUPLING FORECAST
# ==========================================================

def build_coupling_forecast(
    weather,
    air_quality
):
    """
    Combine hourly weather and air-quality information.

    The result contains up to 72 hourly records.

    Each record contains:

        Weather
        Air quality
        PBL height
        Inversion proxy
        Dispersion score
        Accumulation risk
    """

    weather_hourly = weather.get(
        "hourly",
        {}
    )

    air_hourly = air_quality.get(
        "hourly",
        {}
    )

    times = weather_hourly.get(
        "time",
        []
    )

    results = []

    # ------------------------------------------------------
    # Limit to 72 hours
    # ------------------------------------------------------

    total_hours = min(
        72,
        len(times)
    )

    for i in range(total_hours):

        timestamp = times[i]

        # ==================================================
        # WEATHER
        # ==================================================

        temperature = safe_number(
            get_hourly_value(
                weather_hourly,
                "temperature_2m",
                i
            )
        )

        humidity = safe_number(
            get_hourly_value(
                weather_hourly,
                "relative_humidity_2m",
                i
            )
        )

        pressure = safe_number(
            get_hourly_value(
                weather_hourly,
                "pressure_msl",
                i
            )
        )

        wind_speed = safe_number(
            get_hourly_value(
                weather_hourly,
                "wind_speed_10m",
                i
            )
        )

        wind_direction = safe_number(
            get_hourly_value(
                weather_hourly,
                "wind_direction_10m",
                i
            )
        )

        precipitation = safe_number(
            get_hourly_value(
                weather_hourly,
                "precipitation",
                i
            )
        )

        pbl_height = safe_number(
            get_hourly_value(
                weather_hourly,
                "boundary_layer_height",
                i
            )
        )

        # ==================================================
        # UPPER-LEVEL TEMPERATURE / HEIGHT
        # ==================================================

        temperature_1000 = get_hourly_value(
            weather_hourly,
            "temperature_1000hPa",
            i
        )

        temperature_925 = get_hourly_value(
            weather_hourly,
            "temperature_925hPa",
            i
        )

        height_1000 = get_hourly_value(
            weather_hourly,
            "geopotential_height_1000hPa",
            i
        )

        height_925 = get_hourly_value(
            weather_hourly,
            "geopotential_height_925hPa",
            i
        )

        # ==================================================
        # AIR QUALITY
        # ==================================================

        pm25 = get_hourly_value(
            air_hourly,
            "pm2_5",
            i
        )

        pm10 = get_hourly_value(
            air_hourly,
            "pm10",
            i
        )

        no2 = get_hourly_value(
            air_hourly,
            "nitrogen_dioxide",
            i
        )

        ozone = get_hourly_value(
            air_hourly,
            "ozone",
            i
        )

        # ==================================================
        # INVERSION / STABILITY
        # ==================================================

        inversion = calculate_inversion_proxy(

            temperature_1000,

            temperature_925,

            height_1000,

            height_925

        )

        # ==================================================
        # DISPERSION
        # ==================================================

        dispersion = calculate_dispersion_score(

            wind_speed,

            pbl_height,

            precipitation

        )

        # ==================================================
        # ACCUMULATION
        # ==================================================

        accumulation = calculate_accumulation_risk(

            wind_speed,

            pbl_height,

            inversion["score"],

            precipitation

        )

        # ==================================================
        # FINAL RECORD
        # ==================================================

        results.append({

            "time": timestamp,

            "temperature": temperature,

            "humidity": humidity,

            "pressure": pressure,

            "wind_speed": wind_speed,

            "wind_direction": wind_direction,

            "precipitation": precipitation,

            "pbl_height": pbl_height,

            "pm25": pm25,

            "pm10": pm10,

            "no2": no2,

            "ozone": ozone,

            "inversion": inversion,

            "dispersion": dispersion,

            "accumulation": accumulation

        })

    return results