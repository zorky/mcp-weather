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

from dotenv import load_dotenv

from agno.agent import RunResponse

# from agno.tools.reasoning import ReasoningTools
# from agno.utils.pprint import pprint_run_response

from agent.agent import create_agent

from tools.crypto_price import get_crypto_price
from utils.metrics_agno import print_metrics_agent

load_dotenv()
LLM_MODEL = os.getenv("LLM_MODEL", "mistral")
LLM_API = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/")
LLM_TEMPERATURE = os.getenv("LLM_TEMPERATURE", '0')  # 0 : déterministe et précis, 0.3 : un peu plus créatif, etc

if __name__ == "__main__":
    question="Quel est le cours du BTC et de l'ETH ?"
    print(f"Agent simple pour le cours de crypto monnaies sur la question : {question}")
    print(f"LLM_MODEL: {LLM_MODEL} {LLM_API} {LLM_TEMPERATURE}")
        
    crypto_agent = create_agent(name="Expert cours de crypto monnaies",                                
                                role="Assistant pour donner le cours de crypto monnaies",
                                tools=[get_crypto_price],                                
                                instructions=[
                                    "Tu es un assistant financier sur les cryptos monnaies.",
                                    "Tu réponds toujours en français, en langage naturel, sans jamais afficher de code, JSON ou d'appels de fonctions.",
                                    "Tu réponds uniquement sur le cours d'un ou plusieurs cryptomonnaies."
                                ]
    )
    crypto_agent.print_response(question, 
                                stream=False, show_full_reason=False)
    # crypto_agent.run(
    #     "Quel est le cours du BTC et de l'ETH ?", stream=False
    # )
    
    print_metrics_agent(crypto_agent)
    # response: RunResponse = crypto_agent.run("Quel est le cours du BTC et de l'ETH ?", stream=False)
    # print(f"** response : {response}")
    # print(f"** response content : {response.content}")
    # pprint_run_response(response, markdown=True)

