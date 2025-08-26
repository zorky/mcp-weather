import requests
from agno.tools import tool

import logging
from logger import init_logger
logger = init_logger(level=logging.DEBUG)


# @tool(show_result=True, stop_after_tool_call=True)
def get_coordinates_openmeteo(city: str) -> tuple:
    """Récupère les coordonnées GPS d'une ville donnée sous forme de (latitude, longitude)."""
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
    # https://geocoding-api.open-meteo.com/v1/search?name=Paris&count=1
    logger.debug(f"get_coordinates_openmeteo : {url}")
    r = requests.get(url)
    data = r.json()
    if results := data.get("results"):
        return results[0]["latitude"], results[0]["longitude"]
    else:
        return "Ville inconnue", "Ville inconnue"

@tool
def get_coordinates_openstreetmap(city: str) -> tuple:
    """Récupère la latitude et la longitude d'une ville à l'aide de l'API Nominatim d'OpenStreetMap."""

    """
    Args:
        city (str): Le nom de la ville.

    Returns:
        dict: Un dictionnaire contenant la latitude et la longitude.
    """
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": city,
        "format": "json",
        "limit": 1
    }

    headers = {
        "User-Agent": "MCPGeocodingTool/1.0"
    }

    response = requests.get(url, params=params, headers=headers)
    if response.status_code != 200:
        return f"Erreur de géocodage pour {city}."

    data = response.json()
    if not data:
        return f"Aucune coordonnée trouvée pour {city}."

    latitude = data[0]["lat"]
    longitude = data[0]["lon"]
    print(f"Coordonnées de {city} : latitude = {latitude}, longitude = {longitude}")
    return latitude, longitude
