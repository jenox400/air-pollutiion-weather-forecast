from src.risk_engine import calculate_overall_risk


result = calculate_overall_risk(

    pm25=80,

    pm10=120,

    temperature=39,

    wind_speed=4

)


print()
print("=" * 50)
print("ENVIRONMENTAL RISK TEST")
print("=" * 50)

print()

print(
    "Overall:",
    result["overall_level"]
)

print(
    "Score:",
    result["overall_score"]
)

print()

print(
    "Concerns:",
    result["concerns"]
)

print()

print(
    "PM2.5:",
    result["pm25"]
)

print()

print(
    "PM10:",
    result["pm10"]
)

print()

print(
    "Temperature:",
    result["temperature"]
)

print()

print(
    "Wind:",
    result["wind"]
)

print()