from langchain.tools import tool
import requests

@tool
def get_jours_feries(annee: int = 2025) -> str:
    """Retourne les jours fériés en France métropolitaine pour une année donnée."""
    url = f"https://calendrier.api.gouv.fr/jours-feries/metropole/{annee}.json"
    response = requests.get(url).json()
    return "\n".join([f"{date} : {nom}" for date, nom in response.items()])

@tool
def get_vacances_scolaires(zone: str = "B", annee: str = "2025") -> str:
    """Retourne les vacances scolaires pour une zone donnée (A, B ou C).
    Zones scolaires en France :
    - Zone A : Académies Besançon, Bordeaux, Clermont-Ferrand, Dijon, Grenoble, Limoges, Lyon, Poitiers
    - Zone B : Académies de Aix-Marseille, Amiens, Caen, Lille, Nancy-Metz, Nantes, Nice, Orléans-Tours, Reims, Rouen, Strasbourg
    - Zone C : Académies de Créteil, Montpellier, Paris, Toulouse, Versailles.
    """
    url = "https://data.education.gouv.fr/api/records/1.0/search/"
    params = {
        "dataset": "fr-en-calendrier-scolaire",
        "rows": 100,
        "q": f"zone:{zone} AND annee_scolaire:{annee}"
    }
    response = requests.get(url, params=params).json()
    vacances = [
        f"{rec['fields']['description']} : du {rec['fields']['start_date'][:10]} au {rec['fields']['end_date'][:10]}"
        for rec in response.get("records", [])
    ]
    return "\n".join(vacances) if vacances else "Aucune donnée trouvée."