import requests


def get_neighborhood_name(latitude, longitude):
    """Return a Korean neighborhood-level name for WGS84 coordinates."""
    if latitude is None or longitude is None:
        return None

    try:
        response = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={
                "lat": float(latitude),
                "lon": float(longitude),
                "format": "jsonv2",
                "accept-language": "ko",
                "zoom": 18,
            },
            headers={"User-Agent": "ANAVI-weather-assistant/1.0"},
            timeout=5,
        )
        response.raise_for_status()
        address = response.json().get("address", {})

        preferred_keys = (
            "neighbourhood",
            "quarter",
            "suburb",
            "village",
            "town",
            "city_district",
        )
        candidates = [address.get(key) for key in preferred_keys]

        for name in candidates:
            if name and name.endswith(("동", "읍", "면", "리")):
                return name
        return next((name for name in candidates if name), None)
    except (requests.RequestException, ValueError, TypeError):
        return None
