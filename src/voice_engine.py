"""
AIR-COUPLE Voice Question Engine

Converts natural-language questions into intents
and generates answers from the forecast data.

Speech recognition itself will be handled by the browser.
"""

import re
from datetime import datetime


# ==========================================================
# QUESTION INTENTS
# ==========================================================

INTENTS = {

    "weather_tomorrow": [
        "kal ka mausam",
        "kal mausam",
        "kal weather",
        "tomorrow weather",
        "weather tomorrow",
        "mausam kal",
    ],

    "rain_start": [
        "baarish kab shuru",
        "barish kab shuru",
        "baarish kab hogi",
        "barish kab hogi",
        "rain kab start",
        "rain when start",
        "when will it rain",
        "when will rain start",
    ],

    "rain_end": [
        "baarish kab tak",
        "barish kab tak",
        "baarish kab rukegi",
        "barish kab rukegi",
        "rain kab tak",
        "rain when stop",
        "when will rain stop",
        "when will rain end",
    ],

    "rain_forecast": [
        "baarish",
        "barish",
        "rain",
        "rainfall",
    ],

    "pollution_forecast": [
        "pollution",
        "air quality",
        "hawa kaisi",
        "hawa ki quality",
        "air kaisi",
        "pradushan",
    ],

    "pm25": [
        "pm2.5",
        "pm 2.5",
        "pm25",
        "particulate",
    ],

    "aqi": [
        "aqi",
        "air quality index",
        "air quality score",
    ],

    "safe_outdoor": [
        "bahar jaana safe",
        "bahar jana safe",
        "bahar ja sakte",
        "bahar jana theek",
        "outside safe",
        "go outside",
        "outdoor safe",
        "outdoor activity",
    ],

    "jogging": [
        "jogging",
        "running",
        "exercise",
        "morning walk",
        "walk",
        "run",
    ],

    "why_pollution": [
        "pollution kyun",
        "pollution kyu",
        "pollution why",
        "why pollution",
        "pollution increasing",
        "pollution badh",
        "pollution increase",
    ],
}


# ==========================================================
# NORMALIZE QUESTION
# ==========================================================

def normalize_text(text):

    if not text:
        return ""

    text = str(text).lower().strip()

    text = re.sub(
        r"[^\w\s\.\-]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text


# ==========================================================
# DETECT INTENT
# ==========================================================

def detect_intent(text):

    original_question = text

    text = normalize_text(text)

    if not text:
        return {
            "intent": "unknown",
            "confidence": "low",
            "question": original_question
        }

    priority = [
        "rain_start",
        "rain_end",
        "weather_tomorrow",
        "pollution_forecast",
        "safe_outdoor",
        "why_pollution",
        "jogging",
        "pm25",
        "aqi",
        "rain_forecast",
    ]

    best_intent = "unknown"
    best_score = 0

    for intent in priority:

        phrases = INTENTS.get(
            intent,
            []
        )

        score = 0

        for phrase in phrases:

            if phrase in text:

                score += len(
                    phrase.split()
                )

        if score > best_score:

            best_score = score
            best_intent = intent

    if best_score >= 3:

        confidence = "high"

    elif best_score >= 1:

        confidence = "medium"

    else:

        confidence = "low"

    return {
        "intent": best_intent,
        "confidence": confidence,
        "question": original_question
    }


# ==========================================================
# FIND RAIN EVENTS
# ==========================================================

def find_rain_events(
    forecast,
    minimum_rain=0.1
):

    events = []

    if not forecast:
        return events

    raining = False
    start_time = None

    for item in forecast:

        rain = item.get(
            "precipitation",
            0
        )

        try:
            rain = float(
                rain or 0
            )

        except (
            TypeError,
            ValueError
        ):
            rain = 0

        is_raining = (
            rain >= minimum_rain
        )

        if is_raining and not raining:

            start_time = item.get(
                "time"
            )

            raining = True

        elif not is_raining and raining:

            events.append({
                "start": start_time,
                "end": item.get("time")
            })

            raining = False
            start_time = None

    if raining and forecast:

        events.append({
            "start": start_time,
            "end": forecast[-1].get("time")
        })

    return events


# ==========================================================
# FORMAT TIME
# ==========================================================

def format_time(timestamp):

    if not timestamp:
        return "unknown time"

    try:

        dt = datetime.fromisoformat(
            timestamp
        )

        return dt.strftime(
            "%I:%M %p"
        ).lstrip("0")

    except (
        ValueError,
        TypeError
    ):

        return str(timestamp)


# ==========================================================
# FORMAT DATE + TIME
# ==========================================================

def format_datetime(timestamp):

    if not timestamp:
        return "unknown time"

    try:

        dt = datetime.fromisoformat(
            timestamp
        )

        result = dt.strftime(
            "%d %b at %I:%M %p"
        )

        return result.lstrip("0")

    except (
        ValueError,
        TypeError
    ):

        return str(timestamp)


# ==========================================================
# WEATHER ANSWER
# ==========================================================

def answer_weather_question(
    forecast,
    location_name="this location"
):

    if not forecast:

        return (
            "I don't have enough weather "
            "forecast data for this location "
            "right now."
        )

    first_24 = forecast[:24]

    temperatures = []
    rain_total = 0

    for item in first_24:

        temperature = item.get(
            "temperature"
        )

        if temperature is not None:

            try:

                temperatures.append(
                    float(temperature)
                )

            except (
                TypeError,
                ValueError
            ):
                pass

        rain = item.get(
            "precipitation",
            0
        )

        try:

            rain_total += float(
                rain or 0
            )

        except (
            TypeError,
            ValueError
        ):
            pass

    if temperatures:

        minimum = min(
            temperatures
        )

        maximum = max(
            temperatures
        )

        answer = (
            f"Tomorrow in {location_name}, "
            f"the temperature may range from "
            f"approximately {minimum:.0f} "
            f"to {maximum:.0f} degrees Celsius."
        )

    else:

        answer = (
            f"I have the forecast for "
            f"{location_name}, but temperature "
            f"data is currently unavailable."
        )

    if rain_total > 0:

        answer += (
            " Rain is also possible during "
            "the forecast period."
        )

    else:

        answer += (
            " No significant rainfall is "
            "currently forecast during this period."
        )

    return answer


# ==========================================================
# RAIN ANSWER
# ==========================================================

def answer_rain_question(
    forecast,
    location_name="this location",
    question_type="rain_forecast"
):

    events = find_rain_events(
        forecast
    )

    if not events:

        return (
            f"No significant rainfall is "
            f"currently forecast for "
            f"{location_name} in the available "
            f"forecast period."
        )

    first_event = events[0]

    start = format_datetime(
        first_event.get("start")
    )

    end = format_datetime(
        first_event.get("end")
    )

    if question_type == "rain_start":

        return (
            f"Rain is currently forecast to "
            f"start around {start} in "
            f"{location_name}."
        )

    if question_type == "rain_end":

        return (
            f"The forecast rain period is "
            f"currently expected to continue "
            f"until around {end} in "
            f"{location_name}."
        )

    return (
        f"Rain is forecast in {location_name}. "
        f"The first forecast rain period is "
        f"around {start}."
    )


# ==========================================================
# POLLUTION ANSWER
# ==========================================================

def answer_pollution_question(
    forecast,
    location_name="this location"
):

    if not forecast:

        return (
            "I don't have enough air-quality "
            "forecast data right now."
        )

    values = []

    for item in forecast[:24]:

        value = item.get(
            "pm25"
        )

        if value is not None:

            try:

                values.append(
                    float(value)
                )

            except (
                TypeError,
                ValueError
            ):
                pass

    if not values:

        return (
            f"Air-quality forecast data for "
            f"{location_name} is currently "
            f"unavailable."
        )

    minimum = min(values)
    maximum = max(values)

    return (
        f"For the next 24 hours in "
        f"{location_name}, PM2.5 is forecast "
        f"to range approximately from "
        f"{minimum:.1f} to {maximum:.1f} "
        f"micrograms per cubic metre. "
        f"Check the latest AQI and health "
        f"advisory before prolonged outdoor "
        f"activity."
    )


# ==========================================================
# OUTDOOR ACTIVITY ANSWER
# ==========================================================

def answer_outdoor_question(
    forecast,
    location_name="this location"
):

    if not forecast:

        return (
            "I don't have enough information "
            "to assess outdoor conditions right now."
        )

    first = forecast[0]

    accumulation = (
        first.get(
            "accumulation",
            {}
        ) or {}
    )

    dispersion = (
        first.get(
            "dispersion",
            {}
        ) or {}
    )

    accumulation_level = (
        accumulation.get(
            "level",
            "Unknown"
        )
    )

    dispersion_level = (
        dispersion.get(
            "level",
            "Unknown"
        )
    )

    if accumulation_level == "High":

        return (
            f"Outdoor conditions in "
            f"{location_name} may be unfavorable "
            f"because pollution accumulation "
            f"potential is currently high. "
            f"Consider reducing prolonged or "
            f"strenuous outdoor activity."
        )

    if dispersion_level == "Low":

        return (
            f"Outdoor conditions in "
            f"{location_name} require caution. "
            f"Pollution dispersion is currently "
            f"limited, so prolonged outdoor "
            f"activity may be less suitable."
        )

    return (
        f"Current atmospheric conditions in "
        f"{location_name} appear relatively "
        f"favorable for pollution dispersion. "
        f"Still check the latest AQI before "
        f"prolonged outdoor activity."
    )


# ==========================================================
# WHY POLLUTION ANSWER
# ==========================================================

def answer_why_pollution(
    forecast,
    location_name="this location"
):

    if not forecast:

        return (
            "I don't have enough atmospheric "
            "data to explain the pollution "
            "conditions right now."
        )

    first = forecast[0]

    reasons = []

    wind = first.get(
        "wind_speed"
    )

    pbl = first.get(
        "pbl_height"
    )

    inversion = (
        first.get(
            "inversion",
            {}
        ) or {}
    )

    if wind is not None:

        try:

            if float(wind) < 4:

                reasons.append(
                    "wind speeds are weak"
                )

        except (
            TypeError,
            ValueError
        ):
            pass

    if pbl is not None:

        try:

            if float(pbl) < 700:

                reasons.append(
                    "the atmospheric boundary "
                    "layer is relatively shallow"
                )

        except (
            TypeError,
            ValueError
        ):
            pass

    if inversion.get(
        "level"
    ) in (
        "Strong",
        "Moderate"
    ):

        reasons.append(
            "atmospheric stability may be "
            "limiting vertical mixing"
        )

    if not reasons:

        return (
            f"The available atmospheric "
            f"indicators for {location_name} "
            f"do not currently show a strong "
            f"pollution-trapping signal."
        )

    reason_text = ", ".join(
        reasons
    )

    return (
        f"Pollution may be accumulating in "
        f"{location_name} because {reason_text}. "
        f"These conditions can reduce the "
        f"dispersion of pollutants near the "
        f"surface."
    )


# ==========================================================
# MAIN QUESTION ANSWER
# ==========================================================

def answer_question(
    question,
    forecast,
    location_name="this location"
):

    detected = detect_intent(
        question
    )

    intent = detected["intent"]

    if intent == "weather_tomorrow":

        answer = answer_weather_question(
            forecast,
            location_name
        )

    elif intent == "rain_start":

        answer = answer_rain_question(
            forecast,
            location_name,
            "rain_start"
        )

    elif intent == "rain_end":

        answer = answer_rain_question(
            forecast,
            location_name,
            "rain_end"
        )

    elif intent == "rain_forecast":

        answer = answer_rain_question(
            forecast,
            location_name,
            "rain_forecast"
        )

    elif intent == "pollution_forecast":

        answer = answer_pollution_question(
            forecast,
            location_name
        )

    elif intent == "pm25":

        answer = answer_pollution_question(
            forecast,
            location_name
        )

    elif intent == "aqi":

        answer = answer_pollution_question(
            forecast,
            location_name
        )

    elif intent == "safe_outdoor":

        answer = answer_outdoor_question(
            forecast,
            location_name
        )

    elif intent == "jogging":

        answer = answer_outdoor_question(
            forecast,
            location_name
        )

    elif intent == "why_pollution":

        answer = answer_why_pollution(
            forecast,
            location_name
        )

    else:

        answer = (
            "I can help with weather, rainfall, "
            "air quality, PM2.5, AQI, outdoor "
            "activity and pollution conditions. "
            "Please ask your question in English, "
            "Hindi or Hinglish."
        )

    return {
        "intent": intent,
        "confidence": detected["confidence"],
        "question": question,
        "answer": answer
    }