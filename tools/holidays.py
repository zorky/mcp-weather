from agno.tools import tool
from pydantic import BaseModel, Field
import requests
import logging
from logger import init_logger
logger = init_logger(level=logging.DEBUG)

class VacancesInput(BaseModel):
    city: str = Field(default="Paris", description="La ville pour laquelle obtenir les vacances scolaires (ex: Paris, Lyon, Marseille)")
    annee_scolaire: str = Field(
            default="2024-2025",
        description="Année scolaire au format 'YYYY-YYYY' (ex: 2024-2025)"
    )

@tool(show_result=True, stop_after_tool_call=True)
def get_jours_feries(annee: int = 2025) -> str:
    """Retourne les jours fériés en France métropolitaine pour une année donnée."""
    url = f"https://calendrier.api.gouv.fr/jours-feries/metropole/{annee}.json"
    response = requests.get(url).json()
    return "\n".join([f"{date} : {nom}" for date, nom in response.items()])

@tool(show_result=True, stop_after_tool_call=True)
def get_vacances_scolaires(city: str, annee_scolaire: str) -> str:
    """Retourne les vacances scolaires pour une ville / commune donnée."""

    """
    Tests : https://data.education.gouv.fr/explore/dataset/fr-en-calendrier-scolaire/api/?disjunctive.description&disjunctive.population&disjunctive.location&disjunctive.zones&disjunctive.annee_scolaire&sort=-end_date&lang=fr&timezone=Europe%2FParis&refine.location=Lyon&exclude.population=Enseignants
    > https://data.education.gouv.fr/api/records/1.0/search/?dataset=fr-en-calendrier-scolaire&q=&sort=-start_date&facet=description&facet=start_date&facet=end_date&facet=annee_scolaire&refine.location=Paris&refine.annee_scolaire=2024-2025
    
    https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-calendrier-scolaire/records?limit=20&refine=location%3A%22Paris%22&refine.annee_scolaire=2024-2025
    Zones scolaires en France :
    - Zone A : Académies Besançon, Bordeaux, Clermont-Ferrand, Dijon, Grenoble, Limoges, Lyon, Poitiers
    - Zone B : Académies de Aix-Marseille, Amiens, Caen, Lille, Nancy-Metz, Nantes, Nice, Orléans-Tours, Reims, Rouen, Strasbourg
    - Zone C : Académies de Créteil, Montpellier, Paris, Toulouse, Versailles.
    """
    logger.debug(f"Récupération des vacances scolaires pour {city} pour l'année scolaire {annee_scolaire}")
    url = "https://data.education.gouv.fr/api/records/1.0/search/"
    params = {
        "dataset": "fr-en-calendrier-scolaire",
        "q": "",
        "sort": "-start_date",
        "facet": ["description", "start_date", "end_date", "annee_scolaire"],
        "rows": 100,
        # "refine.zone": zone,
        "refine.location": city,
        "refine.annee_scolaire": annee_scolaire,
    }
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    data = r.json().get("records", [])
    if not data:
        return f"Aucune donnée pour {city}, année {annee_scolaire}."
    lignes = []
    for rec in data:
        f = rec.get("fields", {})
        debut = str(f.get("start_date", ""))[:10]
        fin = str(f.get("end_date", ""))[:10]
        desc = f.get("description", "Vacances")
        lignes.append(f"{desc} : du {debut} au {fin}")
    return "\n".join(sorted(set(lignes)))