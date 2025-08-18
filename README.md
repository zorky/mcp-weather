# Expérimentation Agent et tools en local

## Tools avec LangChain en python

> Branche https://github.com/zorky/mcp-weather/tree/mcp-weather-ollama-langchain

- LangChain pour le chainage de traitement des tools en mode ReAct (Reasoning and Acting)
- Ollama pour le serveur local LLM : .env pour choisir le modèle, par défaut `mistral`
- FastAPI pour l'API /ask
- Streamlit pour l'interface web
- docker avec 2 images à construire : agent-tools et streamlit-tools

### Sources, branche et lancer

- git clone git@github.com:zorky/mcp-weather.git
- cd mcp-weather
- git switch mcp-weather-ollama-langchain
- docker compose build
- docker compose up


