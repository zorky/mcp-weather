# agent_meteo.py
import requests
from datetime import datetime
from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.tools import tool
from ollama import Client
from textwrap import dedent
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from logger import init_logger
logger = init_logger(level=logging.DEBUG)

MODEL="mistral"
LLM_API="http://localhost:11434/"
TEMPERATURE="0.3"

def _get_ollama_model():
    ollama_sync_client = Client(
        host=LLM_API,
        headers={
            'temperature': TEMPERATURE
        }
    )
    ollama_model = Ollama(id=MODEL, provider="Ollama", client=ollama_sync_client)
    return ollama_model

def _transform_date(date_str: str, short = True) -> str:
    """Transforme une date au format 'YYYY-MM-DD' en 'DD/MM/YYYY'."""
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime("%d/%m/%Y")
    except ValueError:
        return date_str  # Retourne la chaîne originale si le format est incorrect
    
# --- Définition du tool météo de prévisions météo ---
@tool(show_result=True, stop_after_tool_call=True)
def get_weather_forecasts(city: str) -> str:
    """
    Retourne les prévisions météo pour une ville donnée en utilisant l'API Open-Meteo,  maximum pour les 6 prochains jours.
    """
    MAX_DAYS=7

    # 1. Géocodage : trouver latitude / longitude
    geo_url = "https://geocoding-api.open-meteo.com/v1/search"
    resp = requests.get(geo_url, params={"name": city, "count": 1})
    data = resp.json()
    logger.debug(f"Appel {geo_url}")
    if "results" not in data or len(data["results"]) == 0:
        return f"Impossible de trouver la ville : {city}"

    lat = data["results"][0]["latitude"]
    lon = data["results"][0]["longitude"]    
    logger.debug(f"Géocodage de {city} : lat={lat}, lon={lon}")

    # 2. Récupérer la météo
    weather_url = "https://api.open-meteo.com/v1/forecast"
    response = requests.get(weather_url, params={
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "timezone": "auto"
        # "current_weather": True
    })
    logger.debug(f"Appel {weather_url}")
    # logger.debug(f"Appel {weather_url}\nRésultat météo : {response.json()}")

    if response.status_code != 200:
        return "Erreur de récupération des données météo."
    data = response.json()
    if "daily" not in data:
        return "Pas de données météo disponibles."
    forecast = data["daily"]
    output = "Prévisions météo pour les prochains jours :\n"
    for i in range(min(MAX_DAYS, len(forecast["time"]))):
        day = _transform_date(forecast["time"][i])
        # day = forecast["time"][i]
        t_min = forecast["temperature_2m_min"][i]
        t_max = forecast["temperature_2m_max"][i]
        rain = forecast["precipitation_sum"][i]
        output += f"- {day} : {t_min}°C → {t_max}°C, pluie : {rain} mm\n"
    logger.debug(f"Météo pour {city} : {output.strip()}")
    return output

    # weather = resp.json()["current_weather"]
    
    # temp = weather["temperature"]
    # wind = weather["windspeed"]

    # return f"À {city}, il fait {temp}°C avec un vent de {wind} km/h."

name_tool_forecasts = getattr(get_weather_forecasts, "name", None)
instructions_forecasts = [
    "Tu es un assistant météo",
    f"⚠️ Tu DOIS utiliser le tool {name_tool_forecasts} pour répondre à toute question météo.",
    # "Tu réponds toujours en français, en langage naturel.",
    # "Tu réponds sans jamais afficher de code, de JSON ou d'appels de fonctions.",
    # "Tu réponds toujours en français, en langage naturel, sans jamais afficher de code, de JSON ou d'appels de fonctions.",
    "Ne réponds jamais avec tes propres connaissances sans appeler le tool."
]

# instructions = """
# Tu es un assistant météo.
# ⚠️ Tu DOIS utiliser le tool get_weather pour répondre à toute question météo.
# Ne réponds jamais avec tes propres connaissances sans appeler le tool.
# """

# --- Définition de l'agent ---
agent = Agent(
    model=_get_ollama_model(),
    tools=[get_weather_forecasts],
    # instructions=dedent(instructions),
    instructions=instructions_forecasts,

    add_datetime_to_instructions=True,
    tool_choice="auto", # non supporté par Ollama Client https://github.com/agno-agi/agno/issues/2625
    debug_mode=True,
)


if __name__ == "__main__":
    # Exemple d'utilisation
    question = "Quelle sera la météo à Nantes à 6 jours ?"
    agent.print_response(question, stream=False, show_full_reason=False)
    # for event in agent.run(question, stream=True):
    #     print(event, end="", flush=True)
    
