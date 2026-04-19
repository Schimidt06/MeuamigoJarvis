import requests
import geocoder
from .base import Command


class WeatherCommand(Command):
    intent = "weather"

    def execute(self, entities, sc):
        try:
            g = geocoder.ip("me")
            lat, lon = g.latlng
            url = (
                f"https://api.open-meteo.com/v1/forecast"
                f"?latitude={lat}&longitude={lon}"
                f"&current=temperature_2m"
                f"&daily=precipitation_probability_max"
                f"&forecast_days=3&timezone=auto"
            )
            data = requests.get(url, timeout=5).json()
            temp = data["current"]["temperature_2m"]
            avg_rain = int(sum(data["daily"]["precipitation_probability_max"]) / 3)
            return (
                f"Temperatura atual de {temp} graus Celsius. "
                f"Probabilidade de chuva média de {avg_rain}% nos próximos três dias."
            )
        except Exception as e:
            print(f"[WEATHER] Erro: {e}")
            return "Tive um problema ao acessar os satélites climáticos, senhor."
