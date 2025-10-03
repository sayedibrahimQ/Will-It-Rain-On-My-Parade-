
import requests
def get_city_from_latlon(lat, lon):
    url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
    response = requests.get(url, headers={"User-Agent": "django-app"})
    data = response.json()

    # Example structure: data["address"]["city"] or ["town"] or ["village"]
    address = data.get("address", {})
    city = address.get("city") or address.get("town") or address.get("village") or "Unknown"
    return city
