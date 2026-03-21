import os
from langchain.agents import initialize_agent, AgentType
from langchain.schema import SystemMessage
from langchain_community.chat_models import ChatOpenAI

from tools.crypto_price import get_crypto_price
from tools.holidays import get_jours_feries, get_vacances_scolaires
from tools.search_web import duckduckgo_search
from tools.weather_tools import get_weather
from tools.geo_tools import get_coordinates_openmeteo

from dotenv import load_dotenv
load_dotenv() 

# MODEL=os.getenv("MODEL_NAME", "llama3:8b-instruct-q4_K_M")
MODEL=os.getenv("MODEL_NAME", "mistral")
LLM_API=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
LLM_TEMPERATURE=os.getenv("LLM_TEMPERATURE", '0.1')  # 0 : déterministe et précis, 0.3 : un peu plus créatif, etc

tools = [get_weather,
         get_crypto_price,
         get_coordinates_openmeteo,
         get_jours_feries, get_vacances_scolaires,
         duckduckgo_search]
# tools = [get_weather, get_crypto_price]
# tools = [get_weather, get_coordinates_openstreetmap]
# tools = [get_coordinates_openmeteo, get_weather]

# llm -> Ollama ou tout autre LLM compatible LangChain
llm = ChatOpenAI(
    temperature=LLM_TEMPERATURE,
    model=MODEL,
    openai_api_base=LLM_API,
    openai_api_key="dummy-key-ollama",
)

# system_prompt = SystemMessage(content="""Tu es un assistant intelligent et serviable.
                              
# Règles absolues :
# - Tu réponds TOUJOURS en français, peu importe la langue de la question
# - Tu formates tes réponses en Markdown (titres, listes, gras, etc.)
# - Tu n'inventes jamais de données : tu utilises uniquement les outils mis à ta disposition
# - Sois concis et clair
# """)

# agent_kwargs={
#     "system_message": system_prompt,
#     "human_message_template": "{input}\n\n⚠️ Réponds obligatoirement en français et en Markdown.",
# }

# agent = initialize_agent(
#     tools=tools,
#     llm=llm,
#     agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
#     verbose=True,
#     agent_kwargs=agent_kwargs
#     # agent_kwargs={
#     #     "system_message": system_prompt,
#     # }
# )
                            
# # agent inférence -> LangChain Agent : llm + tools
agent = initialize_agent(
    tools=tools,
    llm=llm,
    # agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
)
