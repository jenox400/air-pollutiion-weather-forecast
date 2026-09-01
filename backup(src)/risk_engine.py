"""
Health and environmental risk assessment.

This module does NOT diagnose medical conditions.
It provides explainable environmental-risk information
based on weather and air-quality measurements.
"""


def safe_number(value):
    """
    Convert a value to float safely.
    """

    try:
        return float(value)

    except (TypeError, ValueError):

        return None


def pm25_risk(pm25):
    """
    Assess PM2.5 environmental exposure level.
    """

    pm25 = safe_number(pm25)

    if pm25 is None:
        return {
            "level": "Unknown",
            "score": 0,
            "message": "PM2.5 data is unavailable."
        }


    if pm25 <= 15:

        return {
            "level": "Low",
            "score": 1,
            "message":
                "PM2.5 levels are relatively low."
        }


    if pm25 <= 35:

        return {
            "level": "Moderate",
            "score": 2,
            "message":
                "PM2.5 is elevated and may affect pollution-sensitive people."
        }


    if pm25 <= 55:

        return {
            "level": "High",
            "score": 3,
            "message":
                "Higher PM2.5 exposure may affect sensitive individuals."
        }


    if pm25 <= 150:

        return {
            "level": "Very High",
            "score": 4,
            "message":
                "PM2.5 is substantially elevated. Sensitive individuals should consider reducing prolonged outdoor exposure."
        }


    return {
        "level": "Extremely High",
        "score": 5,
        "message":
            "PM2.5 is extremely elevated. Avoid prolonged outdoor exposure where possible."
    }


def pm10_risk(pm10):
    """
    Assess PM10 environmental exposure level.
    """

    pm10 = safe_number(pm10)

    if pm10 is None:

        return {
            "level": "Unknown",
            "score": 0,
            "message": "PM10 data is unavailable."
        }


    if pm10 <= 45:

        return {
            "level": "Low",
            "score": 1,
            "message":
                "PM10 levels are relatively low."
        }


    if pm10 <= 100:

        return {
            "level": "Moderate",
            "score": 2,
            "message":
                "PM10 is elevated."
        }


    if pm10 <= 150:

        return {
            "level": "High",
            "score": 3,
            "message":
                "High PM10 levels may increase particulate exposure."
        }


    return {
        "level": "Very High",
        "score": 4,
        "message":
            "PM10 is substantially elevated."
    }


def temperature_risk(temperature):
    """
    Assess environmental heat exposure.
    """

    temperature = safe_number(
        temperature
    )

    if temperature is None:

        return {
            "level": "Unknown",
            "score": 0,
            "message":
                "Temperature data is unavailable."
        }


    if temperature < 30:

        return {
            "level": "Low",
            "score": 1,
            "message":
                "Temperature is not unusually high."
        }


    if temperature < 35:

        return {
            "level": "Moderate",
            "score": 2,
            "message":
                "Warm conditions may increase heat discomfort."
        }


    if temperature < 40:

        return {
            "level": "High",
            "score": 3,
            "message":
                "High temperatures may increase heat stress, particularly during prolonged outdoor activity."
        }


    return {
        "level": "Very High",
        "score": 4,
        "message":
            "Very high temperatures can increase heat stress."
    }


def wind_risk(wind_speed):
    """
    Assess ventilation conditions using wind speed.

    Low wind can contribute to pollutant accumulation,
    depending on local conditions.
    """

    wind_speed = safe_number(
        wind_speed
    )

    if wind_speed is None:

        return {
            "level": "Unknown",
            "score": 0,
            "message":
                "Wind data is unavailable."
        }


    if wind_speed >= 10:

        return {
            "level": "Low",
            "score": 1,
            "message":
                "Stronger winds may help disperse pollutants."
        }


    if wind_speed >= 5:

        return {
            "level": "Moderate",
            "score": 2,
            "message":
                "Moderate wind conditions are present."
        }


    return {
        "level": "Elevated",
        "score": 3,
        "message":
            "Low wind conditions may reduce pollutant dispersion."
    }


def calculate_overall_risk(
    pm25,
    pm10,
    temperature,
    wind_speed
):
    """
    Combine environmental factors into an
    explainable overall risk assessment.
    """

    pm25_result = pm25_risk(pm25)

    pm10_result = pm10_risk(pm10)

    temperature_result = temperature_risk(
        temperature
    )

    wind_result = wind_risk(
        wind_speed
    )


    scores = [

        pm25_result["score"],

        pm10_result["score"],

        temperature_result["score"],

        wind_result["score"]

    ]


    overall_score = max(scores)


    if overall_score <= 1:

        level = "Low"


    elif overall_score == 2:

        level = "Moderate"


    elif overall_score == 3:

        level = "High"


    elif overall_score == 4:

        level = "Very High"


    else:

        level = "Extremely High"


    concerns = []


    if pm25_result["score"] >= 3:

        concerns.append(
            "elevated PM2.5"
        )


    if pm10_result["score"] >= 3:

        concerns.append(
            "elevated PM10"
        )


    if temperature_result["score"] >= 3:

        concerns.append(
            "high temperature"
        )


    if wind_result["score"] >= 3:

        concerns.append(
            "low wind / reduced pollutant dispersion"
        )


    return {

        "overall_level": level,

        "overall_score": overall_score,

        "concerns": concerns,

        "pm25": pm25_result,

        "pm10": pm10_result,

        "temperature": temperature_result,

        "wind": wind_result

    }