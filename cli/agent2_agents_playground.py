"""
 Simple script pour tester rapidement les agents en collaboration, avec des métrics

 Lit le fichier .env pour le modèle
 Ollama doit être lancé : $ docker compose up ollama -d
 /!\ le modèle pour Ollama est précisé dans le .env, il doit correspondre à celui utilisé dans agent.py
 Pour le script, l'appel à l'API doit être sur http://localhost a contrario de l'app web du docker-compose (ie : http://ollama)

 $ python cli/agent2_agents_playground.py
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from agno.team.team import Team
from agno.playground import Playground, serve_playground_app
from agno.utils.pprint import pprint_run_response

from utils.metrics_agno import print_metrics_team
from agent.agent import _get_agents_team, get_agent_team

agents = _get_agents_team()
app = Playground(agents=agents).get_app()

if __name__ == "__main__":    
    serve_playground_app("agent2_agents_playground:app", reload=True)
    