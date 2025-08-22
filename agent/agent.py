import os

from tools.crypto_price import get_crypto_price
from tools.holidays import get_jours_feries, get_vacances_scolaires
from tools.weather_tools import get_weather
from tools.geo_tools import get_coordinates_openmeteo

from ollama import Client

from agno.agent import Agent
# from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.googlesearch import GoogleSearchTools
# from agno.tools.reasoning import ReasoningTools
from agno.team.team import Team
from agno.models.ollama import Ollama

import logging
from logger import init_logger
logger = init_logger(level=logging.DEBUG)

MODEL=os.getenv("MODEL_NAME", "mistral")
# MODEL=os.getenv("MODEL_NAME", "llama3:8b-instruct-q4_K_M")
LLM_API=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/")
LLM_TEMPERATURE=os.getenv("LLM_TEMPERATURE", '0.3')  # 0 : déterministe et précis, 0.3 : un peu plus créatif, etc

MODE_TEAM_AGENTS = "coordinate"

def _get_ollama_model():
    ollama_sync_client = Client(
        host=LLM_API,
        headers={
            'temperature': LLM_TEMPERATURE,
            # 'seed': '1234567890'
        }
    )
    ollama_model = Ollama(id=MODEL, provider="Ollama", client=ollama_sync_client)
    return ollama_model

def create_agent(name: str, role: str, tools: list, instructions: str | list[str], /) -> Agent:
    return Agent(
        name=name,
        role=role,
        model=_get_ollama_model(),
        tools=tools,
        instructions=instructions,
        show_tool_calls=False,
        use_json_mode=False,
        markdown=True,
    )

def _get_agents_team():
    weather_agent = Agent(
        name="Expert météo",
        role="Donner des informations météo",
        model=_get_ollama_model(),
        tools=[
            # ReasoningTools(add_instructions=True),
            get_weather],
        instructions="Réponds uniquement sur la météo d'une ville ou d'un lieu.",
        show_tool_calls=True,
        markdown=True,
    )

    crypto_agent = Agent(
        name="Expert cours de crypto monnaies",
        role="Donner le cours de crypto monnaies",
        model=_get_ollama_model(),
        tools=[get_crypto_price],
        instructions="Réponds uniquement sur le cours d'un ou plusieurs cryptomonnaies.",
        show_tool_calls=True,
        markdown=True,
    )

    holidays_agent = Agent(
        name="Expert des dates de vacances scolaires ou de jours fériés",
        role="Donner les dates de vacances scolaires ou de jours fériés pour une ville ou une commune",
        model=_get_ollama_model(),
        tools=[get_jours_feries, get_vacances_scolaires],
        instructions="Réponds uniquement sur les dates de vacances scolaires ou de jours fériés pour une ville ou une commune.",
        show_tool_calls=True,
        markdown=True,
    )

    gps_agent = Agent(
        name="Expert de coordonnées GPS",
        role="Donner les coordonnées GPS d'une ville ou d'une commune",
        model=_get_ollama_model(),
        tools=[get_coordinates_openmeteo],
        instructions="Réponds uniquement sur les demandes de coordonnées GPS pour une ville ou une commune.",
        show_tool_calls=True,
        markdown=True,
    )

    search_agent = Agent(
        name="Web News Agent",
        role="Recherche Web pour les informations n'ayant pas d'expert ou d'agent dédié",
        description="Vous êtes un agent de presse qui aide les utilisateurs à trouver les dernières nouvelles.",
        model=_get_ollama_model(),
        tools=[GoogleSearchTools()],
        # tools=[DuckDuckGoTools()],
        instructions="À partir d'un sujet donné par l'utilisateur, répondez avec les quatre dernières actualités sur ce sujet."
                     "Recherchez 10 actualités et sélectionnez les quatre éléments uniques les plus importants."
                     "Rechercher en français.",
        show_tool_calls=True,
        debug_mode=True,
        markdown=False,
    )
    return [weather_agent, crypto_agent, holidays_agent, gps_agent, search_agent]

def get_agent_team() -> Team:
    """
    Equipe d'agents multi-tools
    """
    logger.debug(f"Création de l'équipe d'agents pour la gestion des outils : {MODEL} {LLM_API} {LLM_TEMPERATURE}")
    team_agent = Team(
        name="Equipe de tools",
        mode=MODE_TEAM_AGENTS,  # coordination : choisit quel agent interroger
        model=_get_ollama_model(),
        members=_get_agents_team(),
        instructions=[
            "Analyse la demande de l'utilisateur et délègue au bon expert ou agent.",
            "Ne mélange pas les domaines : météo → Expert météo, "
            "crypto → Expert cours de crypto monnaies, "
            "vacances scolaires ou fériés → Agent des dates de vacances scolaires ou fériés,"
            "coordonnées GPS → agent de coordonnées GPS,"
            "pour une recherche web ou d'actualités qui n'a pas d'outils → utilise l'agent de recherche Web."
        ],
        show_tool_calls=True,
        markdown=True
    )
    return team_agent