"""
utils/weather.py
OpenWeatherMap API helper with session-state caching.
"""
import time
import requests
import streamlit as st
from .constants import OWM_API_KEY, CACHE_TTL
def get_weather(district: str, lat: float, lon: float, L: dict):
    """
    Fetch weather for a district. Caches in session_state for CACHE_TTL seconds.
    Returns (data_dict, source_label).
    """
    cache_key = f"weather_{district}"
    now = time.time()

    if cache_key in st.session_state:
        cached = st.session_state[cache_key]
        age = now - cached["fetched_at"]
        if age < CACHE_TTL:
            mins_left = int((CACHE_TTL - age) / 60)
            return cached["data"], f"{L['cache']} ({mins_left} min)"

    try:
        url = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?lat={lat}&lon={lon}&appid={OWM_API_KEY}&units=metric"
        )
        r = requests.get(url, timeout=8)
        if r.status_code == 200:
            d = r.json()
            data = {
                "success":     True,
                "temp":        round(d["main"]["temp"], 1),
                "humidity":    round(d["main"]["humidity"], 1),
                "feels_like":  round(d["main"]["feels_like"], 1),
                "wind":        round(d["wind"]["speed"] * 3.6, 1),
                "pressure":    d["main"]["pressure"],
                "description": d["weather"][0]["description"].title(),
                "city":        d.get("name", district),
            }
            st.session_state[cache_key] = {"data": data, "fetched_at": now}
            return data, L["live"]
        return {"success": False, "error": f"HTTP {r.status_code}"}, L["weather_err"]
    except Exception as e:
        return {"success": False, "error": str(e)}, L["weather_err"]
