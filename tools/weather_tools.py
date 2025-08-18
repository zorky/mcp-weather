import logging

import requests
from datetime import datetime

from agno.agent import Agent
from agno.tools import tool

from logger import init_logger
logger = init_logger(level=logging.DEBUG)

from tools.geo_tools import get_coordinates_openmeteo #, get_coordinates_openstreetmap

MAX_DAYS=7

@tool(show_result=True, stop_after_tool_call=True)
def get_weather(city: str) -> str:
    """Renvoie les prévisions météo pour une ville donnée, maximum pour les 6 prochains jours. description obligatoire pour tool"""
    logger.debug(f"Récupération des prévisions météo pour {city}")
    lat, lon = get_coordinates_openmeteo(city)
    logger.debug(f"Latitude : {lat} - Longitude : {lon}")
    # lat, lon = get_coordinates_openstreetmap(city)
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "timezone": "auto"
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return "Erreur de récupération des données météo."
    data = response.json()
    if "daily" not in data:
        return "Pas de données météo disponibles."
    forecast = data["daily"]
    output = "Prévisions météo pour les prochains jours :\n"
    for i in range(min(MAX_DAYS, len(forecast["time"]))):
        # day = _transform_date(forecast["time"][i])
        day = forecast["time"][i]
        t_min = forecast["temperature_2m_min"][i]
        t_max = forecast["temperature_2m_max"][i]
        rain = forecast["precipitation_sum"][i]
        output += f"- {day} : {t_min}°C → {t_max}°C, pluie : {rain} mm\n"
    logger.debug(f"Météo pour {city} : {output.strip()}")
    return output

def _transform_date(date_str: str, short = True) -> str:
    """Transforme une date au format 'YYYY-MM-DD' en 'DD/MM/YYYY'."""
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime("%d/%m/%Y")
    except ValueError:
        return date_str  # Retourne la chaîne originale si le format est incorrect