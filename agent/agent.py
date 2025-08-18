import os
#
# from tools.crypto_price import get_crypto_price
# from tools.holidays import get_jours_feries, get_vacances_scolaires
# from tools.search_web import duckduckgo_search
from tools.weather_tools import get_weather
# from tools.geo_tools import get_coordinates_openmeteo

from ollama import Client
from agno.agent import Agent
from agno.models.ollama import Ollama

MODEL=os.getenv("MODEL_NAME", "llama3:8b-instruct-q4_K_M")
LLM_API=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")

LLM_TEMPERATURE='0.3'  # 0 : déterministe et précis, 0.3 : un peu plus créatif, etc

ollama_sync_client = Client(
    host    = LLM_API,
    headers = {
        'temperature': LLM_TEMPERATURE
    }
)

tools = [get_weather]
# tools = [get_weather,
#          get_crypto_price,
#          get_coordinates_openmeteo,
#          get_jours_feries, get_vacances_scolaires,
#          duckduckgo_search]
# tools = [get_weather, get_crypto_price]
# tools = [get_weather, get_coordinates_openstreetmap]
# tools = [get_coordinates_openmeteo, get_weather]

agent = Agent(
    name="Multi tools agent",
    role="Donner des informations météo",
    model=Ollama(id=MODEL, provider="Ollama", client=ollama_sync_client),
    tools=[get_weather],
    instructions="Utilise les outils disponibles pour fournir la météo",
    show_tool_calls=True,
    markdown=True,
)

