import os
import requests

def get_weather(lat, lon):
    """Fetch weather from OpenWeather."""
    try:
        OPENWEATHER_KEY = os.getenv("OPENWEATHER_API")
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_KEY}&units=metric"
        r = requests.get(url).json()
        return {
            "temperature": f"{r['main']['temp']}°C",
            "condition": r['weather'][0]['main']
        }
    except:
        return {"temperature": "Unknown", "condition": "Unknown"}


# ⭐ NEW — OpenStreetMap Overpass API (Live Nearby Places)
def get_nearby_places_osm(lat, lon, query="cafe"):
    """
    Query the FREE OpenStreetMap Overpass API for nearby places.
    """
    overpass_url = "https://overpass-api.de/api/interpreter"

    q = f"""
    [out:json];
    (
      node["amenity"="{query}"](around:800,{lat},{lon});
      way["amenity"="{query}"](around:800,{lat},{lon});
      relation["amenity"="{query}"](around:800,{lat},{lon});
    );
    out center;
    """

    try:
        res = requests.post(overpass_url, data={"data": q}, timeout=10)
        data = res.json()

        results = []
        for el in data.get("elements", []):
            name = el.get("tags", {}).get("name", "Unnamed Place")
            lat_val = el.get("lat") or el.get("center", {}).get("lat")
            lon_val = el.get("lon") or el.get("center", {}).get("lon")

            results.append({
                "name": name,
                "lat": lat_val,
                "lon": lon_val
            })

        return results[:3]  # return 3 nearest places
    except Exception as e:
        print("OSM ERROR:", e)
        return []


# Fallback store (used only when OSM fails)
def get_nearby_store(lat, lon):
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
        data = requests.get(url, headers={"User-Agent": "ContextOS"}).json()

        display = data.get("display_name", "")
        if "Starbucks" in display:
            name = "Starbucks"
        else:
            name = "Coffee Shop"

        return {"name": name, "distance": "Nearby"}
    except:
        return {"name": "Unknown", "distance": "Unknown"}
