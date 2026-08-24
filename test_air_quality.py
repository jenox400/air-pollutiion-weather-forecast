from src.air_quality_api import get_air_quality


LATITUDE = 28.0229
LONGITUDE = 73.3119


print("Testing Air Quality API...")

data = get_air_quality(
    LATITUDE,
    LONGITUDE
)

print("\nSUCCESS")

print(
    "Number of hourly records:",
    len(data["hourly"]["time"])
)

print("\nFirst timestamp:")
print(data["hourly"]["time"][0])

print("\nFirst PM2.5 value:")
print(data["hourly"]["pm2_5"][0])