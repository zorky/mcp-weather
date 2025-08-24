"""
 Simple script pour tester rapidement les agents, avec des métrics

 Lit le fichier .env pour le modèle
 Ollama doit être lancé : $ docker compose up ollama -d
 /!\ le modèle pour Ollama est précisé dans le .env, il doit correspondre à celui utilisé dans agent.py
 Pour le script, l'appel à l'API doit être sur http://localhost a contrario de l'app web du docker-compose (ie : http://ollama)

 $ python cli/agent1.py
"""

import os
 
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from logger import init_logger
logger = init_logger(level=logging.DEBUG)

from dotenv import load_dotenv

from agno.agent import Agent, RunResponse


from agent.agent import create_agent, _get_ollama_model

from tools.weather_tools import get_weather
from utils.metrics_agno import print_metrics_agent

load_dotenv()
LLM_MODEL = os.getenv("LLM_MODEL", "mistral")
LLM_API = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/")
LLM_TEMPERATURE = os.getenv("LLM_TEMPERATURE", '0')  # 0 : déterministe et précis, 0.3 : un peu plus créatif, etc

if __name__ == "__main__":    
    question="Quelle est la météo sur 6 jours à Paris ?"
    print(f"Agent simple pour la météo d'une ville sur la question : {question}")
    print(f"LLM_MODEL: {LLM_MODEL} {LLM_API} {LLM_TEMPERATURE}")    
    weather_agent = create_agent(
        name="Expert météo",
        role="Donner des informations météo",        
        tools=[get_weather],
        instructions=["Tu es un assistant météo.", 
                      "Tu réponds toujours en français, en langage naturel, sans jamais afficher de code, de JSON ou d'appels de fonctions.", 
                      "Tu donnes uniquement les prévisions météo pour la ville demandée."]
    )  
    weather_agent.print_response(question, 
                                stream=False, show_full_reason=False)
    # response = weather_agent.run(question, stream=False)
    # print(f"** response : {response.content}")
    
    print_metrics_agent(weather_agent)
    


  