# Initialisation environnement python

## UV

```bash
uv venv
source .venv/bin/activate # linux / mac
source .venv/Scripts/activate # windows
uv sync
```

Exemple d'ajout de packages :

```bash
uv add langchain langchain-community langchainhub openai
```

## PIP

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Images Docker 

A part Ollama, 2 images sont utilisées avec le code du dépôt : `agent-tools` et `streamlit`

Les 2 images utilisées dans le docker-compose.yml peuvent être construites 

```bash
$ docker compose build # construit les 2 : agent-tools et streamlit 
$ docker compose build agent-tools # construit uniquement l'image agent-tools
$ docker compose build streamlit # construit uniquement l'image streamlit
```

Lancer l'ensemble :

```bash
$ docker compose up
```

3 images sont disponibles :

```bash
└─ $ ▶ docker ps
CONTAINER ID   IMAGE             COMMAND                  CREATED          STATUS                    PORTS                                             NAMES
3eedb68d1d6f   streamlit-tools   "streamlit run app.p…"   50 minutes ago   Up 50 minutes             0.0.0.0:8501->8501/tcp, [::]:8501->8501/tcp       streamlit
05d574d57a0c   agent-tools       "uvicorn main:app --…"   50 minutes ago   Up 50 minutes             0.0.0.0:8000->8000/tcp, [::]:8000->8000/tcp       agent-tools
c589447fbee0   ollama/ollama     "/bin/sh -c 'ollama …"   50 minutes ago   Up 50 minutes (healthy)   0.0.0.0:11434->11434/tcp, [::]:11434->11434/tcp   ollama
```

# Tools

Tous les tools utilisent des API ne nécessitant pas de clé d'API.

- l'API météo utilisée est : https://open-meteo.com/ - ne nécessite pas de clé d'API, open-meteo permet de récupérer les prévisions météo à 7 jours pour une ville donnée, avec les températures minimales et maximales, ainsi que les précipitations à partir des coordonnées géographiques (latitude et longitude).
- l'API de géocodage sera utilisée pour obtenir les coordonnées GPS : https://nominatim.openstreetmap.org/ (autre alternative : https://geocoding-api.open-meteo.com/v1/search), User-Agent doit être identifié dans les headers de la requête
- l'API des cryptomonnaies : https://min-api.cryptocompare.com/data/price?fsym=BTC&tsyms=EUR&e=CCCAGG
- l'API des jours fériés en France : https://calendrier.api.gouv.fr/jours-feries/metropole/2025.json
- l'API des vacances scolaires en France : https://data.education.gouv.fr/api/records/1.0/search/?dataset=fr-en-calendrier-scolaire&q=&sort=-start_date&facet=description&facet=start_date&facet=end_date&facet=annee_scolaire&refine.location=Paris&refine.annee_scolaire=2024-2025

# Lancer les serveurs

```bash
$ docker compose up
```

OU avec l'environnement virtuel

```bash
cd mcp_server
uvicorn main:app --reload
```

- L'API est disponible à l'adresse suivante : http://127.0.0.1:8000/docs

- L'interface Streamlit à l'adresse suivante : http://localhost:8501/

# Exemples de sorties

Exemple d'appels avec la commande `curl`, sans passer par Streamlit, directement par l'API FastAPI :


```bash
curl -X 'GET' \
  'http://127.0.0.1:8000/ask?question=quel%20est%20le%20temps%20%C3%A0%20Paris%20%3F' \
  -H 'accept: application/json'
```

```bash
curl --get --data-urlencode "question=Quelle est la météo des 3 prochains jours à Bordeaux, France ?" http://127.0.0.1:8000/ask
```

A la question "Quel est le cours du BTC et de l'ETH", avec curl :

```bash
curl -X 'GET' \
  'http://localhost:8000/ask?question=Quel%20est%20le%20cours%20du%20BTC%20et%20de%20l%27ETH' \
  -H 'accept: application/json'
```
Sortie et réponse :

```bash

```