"""
 Simple script pour tester rapidement les agents en collaboration, avec des métrics

 Lit le fichier .env pour le modèle
 Ollama doit être lancé : $ docker compose up ollama -d
 /!\ le modèle pour Ollama est précisé dans le .env, il doit correspondre à celui utilisé dans agent.py
 Pour le script, l'appel à l'API doit être sur http://localhost a contrario de l'app web du docker-compose (ie : http://ollama)

 $ python cli/agent2.py
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from agno.team.team import Team
from agno.utils.pprint import pprint_run_response

from utils.metrics_agno import print_metrics_team
from agent.agent import get_agent_team

if __name__ == "__main__":
    default_question="Je veux partir à Rome la semaine prochaine, quel temps fera-t-il ?"
    question = input("Entrez votre question (ou appuyez sur Entrée pour la question par défaut) : ") or default_question
    print(f"Agent Team multi-agents sur la question {question}")
    team = get_agent_team()
    response = team.run(question, stream=False)
    pprint_run_response(response, markdown=False)
    # print_metrics_team(team)
    