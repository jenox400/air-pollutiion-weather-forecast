import requests


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"


def search_location(city_name):
    """
    Search for a city and return matching locations.
    """

    params = {
        "name": city_name,
        "count": 10,
        "language": "en",
        "format": "json"
    }

    response = requests.get(
        GEOCODING_URL,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    results = data.get("results", [])

    locations = []

    for place in results:

        locations.append({
            "name": place.get("name"),
            "latitude": place.get("latitude"),
            "longitude": place.get("longitude"),
            "country": place.get("country"),
            "state": place.get("admin1")
        })

    return locations