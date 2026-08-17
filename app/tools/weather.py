from langchain.tools import tool
import requests
from app.config import Config
from app.tools.utils import log_tool_call


@tool
@log_tool_call
def get_weather(city: str) -> str:
    """Погода в городе через OpenWeatherMap."""
    if not Config.weather_key: return "Нет ключа"
    r = requests.get("https://api.openweathermap.org/data/2.5/weather",
        params={"q":city,"appid":Config.weather_key,"units":"metric","lang":"ru"}, timeout=10)
    d = r.json()
    if d.get("cod")!=200: return f"Не найден: {city}"
    return f"{d['name']}: {d['weather'][0]['description']}, {round(d['main']['temp'])}°C, влаж {d['main']['humidity']}%, ветер {d['wind']['speed']}м/с"
