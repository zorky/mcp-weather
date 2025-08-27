# agent_meteo.py
from dotenv import load_dotenv
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

from cli.ollama_client_model import LLM_API, MODEL, TEMPERATURE, get_ollama_model

import logging
from logger import init_logger
logger = init_logger(level=logging.DEBUG)

def _transform_date(date_str: str, short = True) -> str:
    """Transforme une date au format 'YYYY-MM-DD' en 'DD/MM/YYYY'."""
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime("%d/%m/%Y")
    except ValueError:
        return date_str  # Retourne la chaîne originale si le format est incorrect

def _get_geo_city(city: str) -> str:
    geo_url = "https://geocoding-api.open-meteo.com/v1/search"
    resp = requests.get(geo_url, params={"name": city, "count": 1})
    data = resp.json()
    logger.debug(f"Appel {geo_url}")
    if "results" not in data or len(data["results"]) == 0:
        return f"Impossible de trouver la ville : {city}"

    lat = data["results"][0]["latitude"]
    lon = data["results"][0]["longitude"]    
    logger.debug(f"Géocodage de {city} : lat={lat}, lon={lon}")
    return lat, lon

def _get_weather(lat, lon, current: bool=False):
    weather_url = "https://api.open-meteo.com/v1/forecast"
    _params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "timezone": "auto"        
    }    
    if current:
        _params['current_weather'] = True
        _params.pop('daily', None)

    logger.debug(f"Appel {weather_url} avec {_params}")  
    response = requests.get(weather_url, params=_params)
    
    if response.status_code != 200:
        return "Erreur de récupération des données météo."  
    return response

# --- Définition du tool météo de prévisions météo ---
@tool(show_result=True, stop_after_tool_call=True)
def get_weather_forecasts(city: str) -> str:
    """
    Retourne les prévisions météo pour une ville donnée en utilisant l'API Open-Meteo,  maximum pour les 6 prochains jours.
    """
    # https://api.open-meteo.com/v1/forecast?latitude=43.70313&longitude=7.26608&daily=temperature_2m_max%2Ctemperature_2m_min%2Cprecipitation_sum&timezone=auto
    MAX_DAYS=7

    # 1. Récupérer les coordonnées GPS de la ville
    lat, lon = _get_geo_city(city)

    # 2. Récupérer la météo    
    response = _get_weather(lat, lon)    
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

@tool(show_result=True, stop_after_tool_call=True)
def get_weather_current(city: str) -> str:
    """
    Retourne les prévisions actuelles météo pour une ville donnée en utilisant l'API Open-Meteo.
    """
    # https://api.open-meteo.com/v1/forecast?latitude=47.21725&longitude=-1.55336&timezone=auto&current_weather=1
    # 1. Récupérer les coordonnées GPS de la ville
    lat, lon = _get_geo_city(city)

    # 2. Récupérer la météo    
    response = _get_weather(lat, lon, current=True)    

    # data = response.json()
    weather = response.json()["current_weather"]
    logger.debug(f"weather {weather}")
    
    temp = weather["temperature"]
    wind = weather["windspeed"]

    return f"À {city}, il fait {temp}°C avec un vent de {wind} km/h."

name_tool_forecasts = getattr(get_weather_forecasts, "name", None)
instructions_forecasts = [
    "Tu es un assistant météo",
    f"⚠️ Tu DOIS utiliser le tool {name_tool_forecasts} pour répondre à toute question météo.",
    # "Tu réponds toujours en français, en langage naturel.",
    # "Tu réponds sans jamais afficher de code, de JSON ou d'appels de fonctions.",
    # "Tu réponds toujours en français, en langage naturel, sans jamais afficher de code, de JSON ou d'appels de fonctions.",
    "Ne réponds jamais avec tes propres connaissances sans appeler le tool."
]
name_tool_current = getattr(get_weather_current, "name", None)
instructions_current = [
    "Tu es un assistant météo",
    f"⚠️ Tu DOIS utiliser le tool {name_tool_current} pour répondre à la météo actuelle.",    
    "Ne réponds jamais avec tes propres connaissances sans appeler le tool."
]

# instructions = """
# Tu es un assistant météo.
# ⚠️ Tu DOIS utiliser le tool get_weather pour répondre à toute question météo.
# Ne réponds jamais avec tes propres connaissances sans appeler le tool.
# """

# --- Définition de l'agent ---
agent = Agent(
    model=get_ollama_model(),
    # tools=[get_weather_forecasts],
    tools=[get_weather_current],    
    # instructions=instructions_forecasts,
    instructions=instructions_current,

    add_datetime_to_instructions=True,
    tool_choice="auto", # non supporté par Ollama Client https://github.com/agno-agi/agno/issues/2625
    debug_mode=True,
)


if __name__ == "__main__":
    logger.debug(f"Création de l'agent météo pour Ollama : {MODEL} {LLM_API} {TEMPERATURE}")
    # default_question="Je veux partir à Rome la semaine prochaine, quel temps fera-t-il ?"
    default_question="Quelle sera la météo à Nantes à 6 jours ?"
    question = input(f"Entrez votre question (ou appuyez sur Entrée pour la question par défaut '{default_question}') : ") or default_question
    print(f"Agent Team multi-agents sur la question : {question}")    
    agent.print_response(question, stream=False, show_full_reason=False)
    # for event in agent.run(question, stream=True):
    #     print(event, end="", flush=True)
    
