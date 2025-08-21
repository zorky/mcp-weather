import os
import logging
from logger import init_logger
logger = init_logger(level=logging.DEBUG)

from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate

from langchain_community.chat_models import ChatOpenAI

from tools.crypto_price import get_crypto_price
from tools.weather_tools import get_weather
from tools.geo_tools import get_coordinates_openmeteo
from tools.holidays import get_jours_feries, get_vacances_scolaires

# from tools.geo_tools import get_coordinates_openmeteo
# from tools.geo_tools import get_coordinates_openstreetmap

MODEL=os.getenv("MODEL_NAME", "llama3:8b-instruct-q4_K_M")
LLM_API=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
LLM_TEMPERATURE=os.getenv("LLM_TEMPERATURE", '0.3')  # 0 : déterministe et précis, 0.3 : un peu plus créatif, etc

# Agent hybride intelligent
def create_hybrid_agent():
    logger.debug("creating hybrid agent")
    logger.debug(f"Utilisation du modèle: {MODEL} sur {LLM_API} avec la temperature {LLM_TEMPERATURE}")
    llm = ChatOpenAI(
        temperature=LLM_TEMPERATURE,
        model=MODEL,
        openai_api_base=LLM_API,
        openai_api_key="dummy-key-ollama",
    )
    tools = [
        Tool(

            name="get_weather",
            func=lambda ville: get_weather(ville),
            description="Obtient les prévisions météo sur plusieurs jours d'une ville. Input: nom de la ville"
        ),
        Tool(
            name="get_crypto_price",
            func=lambda symbol: get_crypto_price(symbol),
            description="Obtient le cour d'une cryptomonnaie. Input: symbole de la cryptomonnaie (ex: BTC, ETH)"
        ),
        Tool(
            name="get_coordinates_openmeteo",
            func=lambda city: get_coordinates_openmeteo(city),
            description="Obtient les coordonnées GPS d'une ville. Input: city : la ville"
        ),
        Tool(
            name="get_jours_feries",
            func=lambda year: get_jours_feries(year),
            description="Obtient jours fériés en France pour une année. Input: year : l'année demandée"
        ),
    ]
    tool_names = ", ".join([tool.name for tool in tools])

    # Prompt hybride permettant connaissances générales + outils
    hybrid_prompt = PromptTemplate.from_template("""
Tu es un assistant intelligent polyvalent. Tu peux :
1. Répondre à des questions générales grâce à tes connaissances
2. Utiliser des outils spécialisés pour des informations spécifiques

Outils disponibles: {tool_names}

{tools}

IMPORTANT:
- Pour les questions générales (histoire, sciences, etc.), réponds directement
- Pour les questions spécifiques (météo, crypto, coordonnées, jours fériés), utilise les outils

Format strict ReAct pour utiliser les outils :
Question: la question d'entrée
Thought: réflexion sur ce qui est demandé
Action: nom exact de l'outil à utiliser parmi [{tool_names}] (si nécessaire, sinon laisse vide)
Action Input: texte brut de l'input de l'outil, sans guillemets ni parenthèses
Observation: résultat de l'outil (si Action utilisé)
Thought: réflexion finale après avoir utilisé l'outil (ou non)
Final Answer: réponse finale complète incluant connaissances générales et résultats d'outils

Begin!

Question: {{input}}
Thought: {agent_scratchpad}
""")

    agent = create_react_agent(llm, tools, hybrid_prompt)

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=5,  # Plus d'itérations pour questions complexes
        return_intermediate_steps=True
    )

    return agent_executor