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


def get_nearby_store(lat, lon):
    """
    FREE fallback: OpenStreetMap reverse search.
    Returns nearest POI name.
    """
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
        data = requests.get(url, headers={"User-Agent": "ContextOS"}).json()

        display = data.get("display_name", "")
        # crude store detection for demo
        if "Starbucks" in display:
            name = "Starbucks"
        else:
            name = "Coffee Shop"

        return {
            "name": name,
            "distance": "Nearby"
        }
    except:
        return {"name": "Unknown", "distance": "Unknown"}
