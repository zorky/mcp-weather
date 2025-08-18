import streamlit as st
import requests
import os

from pydantic import BaseModel
from typing import Optional

AGENT_WEATHER_URL = os.getenv("AGENT_WEATHER_URL", "http://localhost:8000/ask")
TIMEOUT_REQUEST_AGENT = int(os.getenv("TIMEOUT_REQUEST_AGENT", 240))

class AgentResponse(BaseModel):
    response: str
    tool: Optional[str] = None
    metadata: Optional[dict] = None
    
# streamlit page
st.set_page_config(page_title="Agent tools", page_icon="🔧")

st.title("Assistant avec LangChain + Ollama + Tools 🌍")

st.markdown("""
Posez une question, par exemple :

* *Quelle est la météo à Paris sur 6 jours ?*
* *Quel est le prix de BTC et d'ETH ?*
* *Quelles sont les coordonnées GPS de Paris ?*
""")

user_input = st.text_input("Votre question", placeholder="Ex: Quelle est la météo à Lyon dans 2 jours ?")

if st.button("Envoyer") and user_input.strip():
    with st.spinner("Réflexion de l'agent... 🤔"):
        try:
            print(f"Envoi de la question à l'API {AGENT_WEATHER_URL}")
            question = user_input
            response = requests.get(
                AGENT_WEATHER_URL,
                params={"question": question},
                timeout=TIMEOUT_REQUEST_AGENT
            )
    
            if response.status_code == 200:
                data = response.json()
                parsed = AgentResponse(**data)
                answer = parsed.response or "Pas de réponse."
                st.success(answer)
            else:
                st.error(f"Erreur API : {response.status_code}")
        except Exception as e:
            st.error(f"Erreur lors de l'appel à l'API : {e}")
