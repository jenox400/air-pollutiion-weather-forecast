from geopy.geocoders import Nominatim


def get_location(city_name):
    """
    Convert a city name into location information.
    """

    geolocator = Nominatim(
        user_agent="air_pollution_weather_forecast"
    )

    location = geolocator.geocode(city_name)

    if location is None:
        return None

    return {
        "name": location.address,
        "latitude": location.latitude,
        "longitude": location.longitude
    }