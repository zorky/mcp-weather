import os

from tools.crypto_price import get_crypto_price
from tools.holidays import get_jours_feries, get_vacances_scolaires
from tools.weather_tools import get_weather
from tools.geo_tools import tool_coordinates_openmeteo

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

def create_agent(name: str = "", 
                 role: str = "", 
                 tools: list = [], 
                 instructions: str | list[str] = "") -> Agent:
    logger.debug(f"Création de l'agent {name} et instructions {instructions}")
    logger.debug(f"pour Ollama : {MODEL} {LLM_API} {LLM_TEMPERATURE}")
    return Agent(
        # name=name,
        # role=role,        
        model=_get_ollama_model(),
        tools=tools,
        instructions=instructions,
        show_tool_calls=True,
        # use_json_mode=True,
        # markdown=True,
        add_datetime_to_instructions=True,
        tool_choice="auto",  # non supporté par Ollama Client https://github.com/agno-agi/agno/issues/2625
        debug_mode=True
    )

def _get_agents_team():
    name_tool_forecasts = getattr(get_weather, "name", None)  
    instructions_forecasts = [
        "Tu es un assistant météo",
        f"⚠️ Tu DOIS utiliser le tool {name_tool_forecasts} pour répondre à toute question météo.",
        # "Tu réponds toujours en français, en langage naturel.",
        # "Tu réponds sans jamais afficher de code, de JSON ou d'appels de fonctions.",
        # "Tu réponds toujours en français, en langage naturel, sans jamais afficher de code, de JSON ou d'appels de fonctions.",
        "Ne réponds jamais avec tes propres connaissances sans appeler le tool."
        ]
    weather_agent = create_agent(
        tools=[get_weather],
        instructions=instructions_forecasts
    )    
    name_tool_crypto = getattr(get_crypto_price, "name", None)
    instructions_crypto = [
        "Tu es un assistant financier sur les cryptos monnaies.",
        f"⚠️ Tu DOIS utiliser le tool {name_tool_crypto} pour répondre à toute question sur les cryptos monnaies.",
        "Tu réponds uniquement sur le cours d'un ou plusieurs cryptomonnaies.",
        "Ne réponds jamais avec tes propres connaissances sans appeler le tool."
    ]
    crypto_agent = create_agent(
        tools=[get_crypto_price],
        instructions=instructions_crypto
    )    
    name_tool_holidays = getattr(get_vacances_scolaires, "name", None)
    name_tool_off = getattr(get_jours_feries, "name", None)
    holidays_agent = create_agent(
        tools=[get_jours_feries, get_vacances_scolaires],
        instructions=["Tu es un assistant des dates de vacances scolaires ou de jours fériés.", 
                     f"⚠️ Tu DOIS utiliser les tools {name_tool_holidays} ou {name_tool_off} pour répondre à toute question sur les vacances scolaires ou les jours fériés.",
                      "Tu réponds uniquement sur les dates de vacances scolaires ou de jours fériés pour une ville ou une commune.",
                      "Ne réponds jamais avec tes propres connaissances sans appeler l'un des 2 tools."]
    )
    name_tool_gps = getattr(tool_coordinates_openmeteo, "name", None)    
    gps_agent = create_agent(    
        tools=[tool_coordinates_openmeteo],
        instructions=["Tu es un assistant de coordonnées GPS.",      
                      f"⚠️ Tu DOIS utiliser le tool {name_tool_gps} pour répondre à toute question sur les coordonnées GPS.",                
                      "Tu réponds uniquement sur les demandes de coordonnées GPS pour une ville ou une commune.",
                      "Ne réponds jamais avec tes propres connaissances sans appeler le tool."]
    )

    # search_agent = Agent(
    #     name="Web News Agent",
    #     role="Recherche Web pour les informations n'ayant pas d'expert ou d'agent dédié",
    #     description="Vous êtes un agent de presse qui aide les utilisateurs à trouver les dernières nouvelles.",
    #     model=_get_ollama_model(),
    #     tools=[GoogleSearchTools()],
    #     # tools=[DuckDuckGoTools()],
    #     instructions="À partir d'un sujet donné par l'utilisateur, répondez avec les quatre dernières actualités sur ce sujet."
    #                  "Recherchez 10 actualités et sélectionnez les quatre éléments uniques les plus importants."
    #                  "Rechercher en français.",
    #     show_tool_calls=True,
    #     debug_mode=True,
    #     markdown=False,
    # )
    return [weather_agent, crypto_agent, holidays_agent, gps_agent, 
            # search_agent
            ]

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
            "Tu réponds toujours en français, en langage naturel, sans jamais afficher de code, JSON ou d'appels de fonctions.",
            "Ne mélange pas les domaines : "
            "météo → Assistant météo, "
            "crypto → Assistant financier des cours de crypto monnaies, "
            "vacances scolaires ou fériés → Assistant des dates de vacances scolaires ou fériés,"
            "coordonnées GPS → Assistant de coordonnées GPS"
            # "pour une recherche web ou d'actualités qui n'a pas d'outils → utilise l'agent de recherche Web."
        ],
        show_tool_calls=True,
        markdown=True
    )
    return team_agent