from langchain.tools import tool
from typing import Literal
from pydantic import BaseModel, Field
import requests

class VacancesInput(BaseModel):
    zone: Literal["A","B","C"] = Field(default="C", description="Zone académique (A, B ou C)")
    annee_scolaire: str = Field(
        default="2025-2026",
        description="Année scolaire au format 'YYYY-YYYY' (ex: 2024-2025)"
    )

@tool
def get_jours_feries(annee: int = 2025) -> str:
    """Retourne les jours fériés en France métropolitaine pour une année donnée."""
    url = f"https://calendrier.api.gouv.fr/jours-feries/metropole/{annee}.json"
    response = requests.get(url).json()
    return "\n".join([f"{date} : {nom}" for date, nom in response.items()])

@tool("get_vacances_scolaires", args_schema=VacancesInput)
def get_vacances_scolaires(zone: str, annee_scolaire: str) -> str:
    """Retourne les vacances scolaires pour une zone donnée (A, B ou C)."""

    """
    https://data.education.gouv.fr/api/records/1.0/search/?dataset=fr-en-calendrier-scolaire&refine.annee_scolaire=2024-2025&refine.zone=C
    Zones scolaires en France :
    - Zone A : Académies Besançon, Bordeaux, Clermont-Ferrand, Dijon, Grenoble, Limoges, Lyon, Poitiers
    - Zone B : Académies de Aix-Marseille, Amiens, Caen, Lille, Nancy-Metz, Nantes, Nice, Orléans-Tours, Reims, Rouen, Strasbourg
    - Zone C : Académies de Créteil, Montpellier, Paris, Toulouse, Versailles.
    """
    url = "https://data.education.gouv.fr/api/records/1.0/search/"
    params = {
        "dataset": "fr-en-calendrier-scolaire",
        "rows": 100,
        "refine.zones": zone,
        "refine.annee_scolaire": annee_scolaire,
    }
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    data = r.json().get("records", [])
    if not data:
        return f"Aucune donnée pour zone {zone}, année {annee_scolaire}."
    lignes = []
    for rec in data:
        f = rec.get("fields", {})
        debut = str(f.get("start_date", ""))[:10]
        fin = str(f.get("end_date", ""))[:10]
        desc = f.get("description", "Vacances")
        lignes.append(f"{desc} : du {debut} au {fin}")
    return "\n".join(sorted(set(lignes)))