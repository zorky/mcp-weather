from agno.tools import tool
import requests

@tool
def duckduckgo_search(query: str) -> str:
    """Fait une recherche DuckDuckGo et retourne un résumé ou extrait."""
    url = "https://api.duckduckgo.com"
    params = {"q": query, "format": "json", "no_redirect": 1, "no_html": 1}
    response = requests.get(url, params=params).json()
    return response.get("Abstract", "Pas de résultat trouvé.")