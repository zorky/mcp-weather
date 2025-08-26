# agent_meteo.py
import requests
from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.tools import tool
from ollama import Client
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from logger import init_logger
logger = init_logger(level=logging.DEBUG)

MODEL="mistral"
LLM_API="http://localhost:11434/"
def _get_ollama_model():
    ollama_sync_client = Client(
        host=LLM_API,
        headers={
            'temperature': "0.3"
        }
    )
    ollama_model = Ollama(id=MODEL, provider="Ollama", client=ollama_sync_client)
    return ollama_model

# --- Définition du tool météo ---
@tool(show_result=True, stop_after_tool_call=True)
def get_weather(city: str) -> str:
    """
    Retourne la météo actuelle pour une ville donnée en utilisant l'API Open-Meteo.
    """
    # 1. Géocodage : trouver latitude / longitude
    geo_url = "https://geocoding-api.open-meteo.com/v1/search"
    resp = requests.get(geo_url, params={"name": city, "count": 1})
    data = resp.json()

    if "results" not in data or len(data["results"]) == 0:
        return f"Impossible de trouver la ville : {city}"

    lat = data["results"][0]["latitude"]
    lon = data["results"][0]["longitude"]
    print(f"Géocodage de {city} : lat={lat}, lon={lon}")
    logger.debug(f"Géocodage de {city} : lat={lat}, lon={lon}")
    # 2. Récupérer la météo
    weather_url = "https://api.open-meteo.com/v1/forecast"
    resp = requests.get(weather_url, params={
        "latitude": lat,
        "longitude": lon,
        "current_weather": True
    })
    weather = resp.json()["current_weather"]

    temp = weather["temperature"]
    wind = weather["windspeed"]

    return f"À {city}, il fait {temp}°C avec un vent de {wind} km/h."


# --- Définition de l'agent ---
agent = Agent(
    model=_get_ollama_model(),
    tools=[get_weather],
    instructions="""
Tu es un assistant météo. 
⚠️ Tu DOIS utiliser le tool get_weather pour répondre à toute question météo. 
Ne réponds jamais avec tes propres connaissances sans appeler le tool.
"""
    # instructions="Tu es un assistant qui répond aux questions météo en utilisant le tool météo si nécessaire."
)


if __name__ == "__main__":
    # Exemple d'utilisation
    question = "Quelle sera la météo à Nantes à 6 jours ?"
    agent.print_response(question, stream=False, show_full_reason=False)
    # for event in agent.run(question, stream=True):
    #     print(event, end="", flush=True)
    
